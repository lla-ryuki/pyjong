# sys
import os
import pickle
from typing import List

# ours
from mytypes import TileType


class ShantenNumCalculator :
    def __init__(self, file_path:str = "../data/shanten_table.pickle", record_mode:bool = False) :
        self.file_path = file_path
        self.record_mode = record_mode

        # 向聴数を記録するハッシュテーブルをロード
        if (os.path.exists(self.file_path)) :
            with open(self.file_path, "rb") as f :
                self.shanten_table = pickle.load(f)
        else :
            self.shanten_table = {}
            with open(self.file_path, "wb") as f :
                pickle.dump(self.shanten_table, f)

        # normal handの向聴数計算用．複数のメソッドをまたいで使うのでここで定義．
        self.shanten_num = 8
        self.shanten_temp = 8
        self.opened_sets_num = 0
        self.hand = [0] * 38
        self.pairs_num = 0
        self.tahtsu_num = 0
        self.sets_num = 0


    """
    tuple化した手牌をキーとして用いて向聴テーブルに登録された向聴数を返す
    キーが登録されていなかった場合向聴数を計算してテーブルに登録
    ロン和了の場合は和了牌もhand[]に加えてこのメソッドに渡す
    """
    def get_shanten_nums(self, hand:List[int], opened_sets_num:int) -> (int, int, int) :
        self.hand = hand[:]
        self.opened_sets_num = opened_sets_num

        shanten_nums = self.shanten_table.get(tuple(hand))
        if (shanten_num is None) :
            print("not hit")
            shanten_nums = self._calc_shanten_nums()
            self.shanten_table[key] = shanten_nums
            if self.record_mode :
                with open(self.file_path, "wb") as f :
                    pickle.dump(self.shanten_table, f)

        return shanten_nums


    # 向聴テーブルをダンプ
    def dump_table(self) -> None :
        with open(self.file_path, "wb") as f :
            pickle.dump(self.shanten_table, f)


    # handの向聴数を計算
    def _calc_shanten_nums(self) -> (int, int, int) :
        if self.opened_sets_num > 0 :
            kokushi = 13
            chiitoi = 6
        else :
            kokushi = self._calc_shanten_num_of_kokushi()
            chiitoi = self._calc_shanten_num_of_chiitoi()
        normal = self._calc_shanten_num_of_normal()

        return (normal, chiitoi, kokushi)


    # 国士無双の向聴数を返す
    def _calc_shanten_num_of_kokushi(self) -> int :
        pairs_num = 0
        shanten_num = 13

        for i in (TileType.TERMINALS | TileType.HONORS) :
            if self.hand[i] != 0 : shanten_num -= 1
            if self.hand[i] > 1 and pairs_num == 0 : pairs_num = 1
        shanten_num -= pairs_num

        return shanten_num


    # 七対子の向聴数を返す
    def _calc_shanten_num_of_chiitoi(self) -> int :
        shanten_num = 6
        kind = 0 # 6対子あっても孤立牌がないと聴牌にならないのでそれのチェック用

        for i in range(1,38) :
            if self.hand[i] >= 1 :
                kind += 1
            if self.hand[i] >= 2 :
                shanten_num -= 1
        if kind < 7 :
            shanten_num += 7 - kind

        return shanten_num


    # 通常手の向聴数を返す
    def _calc_shanten_num_of_normal(self) -> int :
        self.shanten_num = 8
        self.pairs_num = 0
        self.tahtsu_num = 0
        self.sets_num = 0

        for i in range(1,38) :
            if self.hand[i] >= 2 :
                self.pairs_num += 1
                self.hand[i] -= 2
                self._pick_out_sets(1)
                self.hand[i] += 2
                self.pairs_num -= 1
        self._pick_out_sets(1)

        return self.shanten_num


    # 面子を抜き出す
    def _pick_out_sets(self, i:int) -> None :
        while i < 38 and self.hand[i] == 0 : i += 1
        if i > 37 :
            self._pick_out_tahtsu(1)
            return
        if self.hand[i] > 2 :
            self.sets_num += 1
            self.hand[i] -= 3
            self._pick_out_sets(i)
            self.hand[i] += 3
            self.sets_num -= 1
        if  i < 28 and self.hand[i+1] > 0 and self.hand[i+2] > 0 :
            self.sets_num += 1
            self.hand[i] -= 1
            self.hand[i+1] -= 1
            self.hand[i+2] -= 1
            self._pick_out_sets(i)
            self.hand[i] += 1
            self.hand[i+1] += 1
            self.hand[i+2] += 1
            self.sets_num -= 1
        self._pick_out_sets(i+1)


    # 塔子を抜き出す
    def _pick_out_tahtsu(self, i:int) -> None :
        while i < 38 and self.hand[i] == 0 : i += 1
        if i > 37 :
            self.shanten_temp = 8 - (self.sets_num + self.opened_sets_num) * 2 - self.tahtsu_num - self.pairs_num
            if self.shanten_temp < self.shanten_num :
                self.shanten_num = self.shanten_temp
            return
        if self.sets_num + self.tahtsu_num < 4 :
            if self.hand[i] == 2 :
                self.tahtsu_num += 1
                self.hand[i] -= 2
                self._pick_out_tahtsu(i)
                self.hand[i] += 2
                self.tahtsu_num -= 1
            if i < 29 and self.hand[i+1] != 0 :
                self.tahtsu_num += 1
                self.hand[i] -= 1
                self.hand[i+1] -= 1
                self._pick_out_tahtsu(i)
                self.hand[i] += 1
                self.hand[i+1] += 1
                self.tahtsu_num -= 1
            if i < 29 and i % 10 < 9 and self.hand[i+2] != 0 :
                self.tahtsu_num += 1
                self.hand[i] -= 1
                self.hand[i+2] -= 1
                self._pick_out_tahtsu(i)
                self.hand[i] += 1
                self.hand[i+2] += 1
                self.tahtsu_num -= 1
        self._pick_out_tahtsu(i+1)
