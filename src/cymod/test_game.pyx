# built-in
import os
import sys
import random
import xml.etree.ElementTree as et

# 3rd
from termcolor import colored
import webbrowser

# ours
from game cimport Game
from player import Player
from shanten import ShantenNumCalculator
from logger import Logger
from mytypes import TileType, BlockType
from yaku cimport *
from yakuman cimport *

# cython
from libcpp cimport bool


cdef class TestGame(Game) :
    cdef public xml
    cdef public log_id
    cdef public tag_name
    cdef public attr
    cdef public bool is_error
    cdef public int i_log
    cdef public int org_got_tile

    def __init__(self, action) :
        super().__init__(action, logging=False, testing=True)
        self.is_error = False


    # 局開始時の初期化
    cdef bool init_subgame(self) :
        cdef int i

        print(colored("Subgame start", "blue", attrs=["bold"]))

        # プレイヤが持つ局に関わるメンバ変数を初期化
        for i in range(4) :
            self.players[i].init_subgame(self.rotations_num)

        self.prevailing_wind = 31 + self.rounds_num    # 場風にあたる牌番号
        self.is_abortive_draw = False                  # 途中流局になるとTrueになる
        self.is_first_turn = True                      # Trueの間は1巡目であることを示す
        self.pao_info = [-1] * 4
        """
        pao_info : [i1, j1, i2, j2]
            1 : 大三元について
            2 : 大四喜について
            i : 鳴いたプレイヤのプレイヤ番号
            j : 鳴かせたプレイヤのプレイヤ番号

        (例)
          pao_info:[-1, -1, 3, 0] -> 0番のプレイヤが3番のプレイヤに4枚目の風牌を鳴かせ大四喜のパオが確定している状態
        """

        # 牌関連
        self.doras = [0] * 5                           # ドラ
        self.dora_indicators = [0] * 5                 # ドラ表示牌
        self.uras = [0] * 5                            # 裏
        self.ura_indicators = [0] * 5                  # 裏表示牌
        self.dora_has_opened = [False] * 5             # ドラの状態, i番目がTrue → dora_indicators[i]がめくれている状態
        self.rinshan_tiles = [0] * 4                   # 嶺上牌
        self.appearing_tiles = [0] * 38                # プレイヤ全員に見えている牌， appearing_tiles[i] が j → i番の牌がj枚見えている
        self.appearing_red_tiles = [False] * 3         # プレイヤ全員に見えている赤牌． 萬子，筒子，索子の順．
        self.wall = [0] * 136                          # 山
        self.remain_tiles_num = 70                     # 山の残り枚数

        # インデックス
        self.i_player = self.rotations_num             # 次のループで行動するプレイヤの番号
        self.i_wall = 0                                # 山用のインデックス
        self.i_rinshan = 0                             # 嶺上牌用のインデックス
        self.i_first_turn = 0                          # 最初の1巡目かどうかを判定するために使うインデックス

        # 和了，点数計算関連
        self.winning_tile = -1                         # 和了牌の牌番号
        self.basic_points = 0                          # 和了の基本点
        self.dealer_wins = False
        self.wins_by_ron = False
        self.wins_by_tenhou = False
        self.wins_by_chiihou = False
        self.wins_by_last_tile = False
        self.wins_by_chankan = False
        self.wins_by_rinshan_kaihou = False
        self.wins_by_pao= False
        self.liability_player = -1
        self.players_wind = -1
        self.temp = [0] * 10                           # 向聴数計算に使う配列
        self.fu = 0                                    # 符の数
        self.han = 0                                   # 翻の数
        self.i_temp = 0                                # temp[]用のindex
        self.fu_temp = 0                               # 符の数（仮）
        self.han_temp = 0                              # 翻の数（仮）
        self.yakuman = 0                               # 役満の数

        # 分岐処理用flag
        self.win_flag = False                          # 局終了判定処理用
        self.ready_flag = False                        # リーチ宣言時の放銃処理用
        self.steal_flag = False                        # 鳴き処理用
        self.dora_opens_flag = False                   # 加槓，大明槓による開槓flag．trueのままゲームが終わらず所定の処理までくるとドラを開けてfalseに戻る
        self.rinshan_draw_flag = False                 # 次のツモが嶺上牌であることを示すflag．trueのままドローフェーズまで来ると嶺上牌をツモってfalseに戻る

        # テスト用
        self.org_got_tile = -1                         # ツモった牌の天鳳牌番号．ツモ切り判定に使う．

        # タグから情報を読んでメンバ変数にセットする
        cdef list starting_hand, seed, ten
        cdef int indicator
        cdef bool error

        # 局の情報に食い違いがあったらエラーとして報告
        print("="*40)
        seed = self.attr["seed"].split(",")
        if (self.rounds_num != int(seed[0]) // 4) or \
           (self.rotations_num != int(seed[0]) % 4) or \
           (self.counters_num != int(seed[1])) or \
           (self.deposits_num != int(seed[2])) and not(self.is_error) : self.error("subgame info (in TestGame.init_subgame())")
        print(f"log_id     : {self.log_id}")
        print(f"round      : {self.rounds_num}")
        print(f"rotation   : {self.rotations_num}")
        print(f"counters   : {self.counters_num}")
        print(f"deposits   : {self.deposits_num}")
        print("")

        # プレイヤの点数に食い違いがあったらエラーとして報告
        ten = self.attr["ten"].split(",")
        error = False
        for i in range(4) :
            print(f"players[{i}].score : {self.players[i].score}")
            print(f"xml_log[{i}].score : {int(ten[i]) * 100}")
        print("="*40)
        for i in range(4) :
            if (self.players[i].score != int(ten[i]) * 100) and (not(self.is_error)) : self.error("score is different (in TestGame.init_subgame())")

        # 配牌を配る
        for i in range(4) :
            starting_hand = [self.convert_tile(int(tile)) for tile in self.attr[f"hai{i}"].split(",")]
            for tile in starting_hand : self.players[i].get_tile(tile)

        # 初期ドラをセット
        indicator = self.convert_tile(int(seed[5]))
        if indicator in TileType.REDS : indicator +=  5
        self.dora_indicators[0] = indicator
        self.dora_has_opened[0] = True
        if indicator in TileType.NINES : self.doras[0] = indicator - 8
        elif indicator == 34 : self.doras[0] = 31
        elif indicator == 37 : self.doras[0] = 35
        else : self.doras[0] = indicator + 1
        self.appearing_tiles[indicator] += 1

        self.read_next_tag()


    # 新しいドラを開く
    # CAUTION テスト管轄外
    cdef void open_new_dora(self) :
        cdef int i, indicator
        for i in range(5) :
            if self.dora_has_opened[i] is False :
                # エラーチェック
                if self.tag_name != "DORA" : self.error("Wrong tag (in TestGame.open_new_dora())")

                # ドラ表示牌をタグから判定
                indicator = self.convert_tile(int(self.attr["hai"]))
                if indicator in TileType.REDS : indicator +=  5

                # ドラ表示牌とドラをセット
                self.dora_indicators[i] = indicator
                if indicator in TileType.NINES : self.doras[i] = indicator - 8
                elif indicator == 34 : self.doras[i] = 31
                elif indicator == 37 : self.doras[i] = 35
                else : self.doras[i] = indicator + 1
                self.appearing_tiles[indicator] += 1
                self.dora_has_opened[i] = True

                self.read_next_tag()
                break


    # 裏ドラをセット
    cpdef void set_ura(self, str uras_s) :
        uras = uras_s.split(",")
        for i, ura in enumerate(uras) :
            indicator = self.convert_tile(int(ura))
            if indicator in TileType.REDS : indicator +=  5
            self.ura_indicators[i] = indicator
            if indicator in TileType.NINES : self.uras[i] = indicator - 8
            elif indicator == 34 : self.uras[i] = 31
            elif indicator == 37 : self.uras[i] = 35
            else : self.uras[i] = indicator + 1


    # 次のツモ牌を返す
    cdef int supply_next_tile(self) :
        cdef int tile
        if self.tag_name[0] not in {"T", "U", "V", "W"} : self.error("Wrong tag (in TestGame.supply_next_tile())")
        org_tile = int(self.tag_name[1:])
        tile = self.convert_tile(org_tile)
        get = colored("get", "green")
        print(f"player{self.i_player} {get} {tile}")
        self.i_wall += 1
        self.remain_tiles_num -= 1
        self.read_next_tag()
        self.org_got_tile = org_tile
        return tile


    # 次の嶺上牌を返す
    cdef int supply_next_rinshan_tile(self) :
        cdef int tile
        if self.tag_name[0] not in {"T", "U", "V", "W"} : self.error("Wrong tag (in TestGame.supply_next_rinshan_tile())")
        org_tile = int(self.tag_name[1:])
        tile = self.convert_tile(org_tile)
        get = colored("get", "green")
        print(f"player{self.i_player} {get} {tile} from rinshan")
        self.i_rinshan += 1
        self.remain_tiles_num -= 1
        self.read_next_tag()
        self.org_got_tile = org_tile
        return tile


    # xml_logの牌番号をこのプログラムの牌番号に変換
    cpdef int convert_tile(self, int org_tile) :
        cdef int tile
        if org_tile in {16, 52, 88} : tile = (org_tile // 40) * 10
        else :
            tile = org_tile // 4
            if tile >= 27 : tile += 4
            elif tile >= 18 : tile += 3
            elif tile >= 9 : tile += 2
            else : tile += 1

        return tile


    # 配牌を配ると言ったなアレは嘘だ
    cdef void deal_starting_hand(self) :
        pass


    # 半荘の処理
    cpdef void play_test_game(self) :
        cdef int i
        while True :
            # 局
            self.init_subgame()
            self.play_subgame()
            # 半荘終了判定
            if self.is_over :
                self.proc_game_end()
                self.check_final_score()
                break


    # テスト用メソッド
    cpdef void test(self) :
        passes_num = 0
        # year = int(input("Input year : "))
        year = 2019
        for month in range(1, 12) :
            # path = f"../data/xml/{year}/{month:02}/"
            home = os.environ["HOME"]
            path = f"{home}/github/ryujin/data/xml/{year}/{month:02}/"
            dir_components = os.listdir(path)
            files = [f for f in dir_components if os.path.isfile(os.path.join(path, f))]
            for file_name in files :
                # 空ファイルが紛れていることがあるのでそれをスキップ
                try : tree = et.parse(path + file_name)
                except : continue

                xml = tree.getroot()
                self.xml = xml[3:]
                self.i_log = 0
                self.read_next_tag()
                self.log_id = file_name[:-4]
                self.init_game()
                print(colored("Game start", "blue", attrs=["bold"]))
                self.play_test_game()
                passes_num += 1
                print(colored(f"{passes_num} files passed!", "green", attrs=["bold"]))
                print("")


    # 単一ファイルテスト用メソッド
    cpdef void partial_test(self, log_id) :
        year = log_id[0:4]
        month = log_id[4:6]
        home = os.environ["HOME"]
        path = f"{home}/github/ryujin/data/xml/{year}/{month}/"
        tree = et.parse(path + log_id + ".xml")
        xml = tree.getroot()
        self.xml = xml[3:]
        self.i_log = 0
        self.read_next_tag()
        self.log_id = log_id
        self.init_game()
        print(colored("Game start", "blue", attrs=["bold"]))
        self.play_test_game()
        print(colored(f"Passed!", "green", attrs=["bold"]))
        print("")


    # プレイヤ全員のscoreを表示
    cpdef void print_scores(self, info) :
        print(colored(info, "yellow", attrs=["bold"]))
        print("="*40)
        for i in range(4) : print(f"players[{i}].score: {self.players[i].score}")
        print("="*40)


    # 和了った時の飜数と符を表示
    cpdef void print_win_info(self, int i_winner, int i_player, int han, int fu, int basic_points) :
        cdef bool dealer_wins
        dealer_wins = i_winner == self.rotations_num
        if i_winner == i_player :
            if i_winner == self.rotations_num :
                points = basic_points * 2
                if points % 100 != 0 : points += (100 - (points % 100))
                points = f"{points} all"
            else :
                points_dealer_pays = self.basic_points * 2
                if points_dealer_pays % 100 != 0 : points_dealer_pays += (100 - (points_dealer_pays % 100))
                points_child_pays = self.basic_points
                if points_child_pays % 100 != 0 : points_child_pays += (100 - (points_child_pays % 100))
                points = (points_child_pays, points_dealer_pays)
        else :
            if dealer_wins : points = basic_points * 6
            else : points = basic_points * 4
            if points % 100 != 0 : points += (100 - (points % 100))


        print(colored("win info", "yellow", attrs=["bold"]))
        print("="*40)
        print(f"dealer   : {dealer_wins}")
        print(f"winner   : {i_winner}")
        if i_winner != i_player : print(f"loser    : {i_player}")
        print(f"han      : {han}")
        print(f"fu       : {fu}")
        print(f"points   : {points}")
        print(f"base_pts : {basic_points}")
        print(f"dora     : {self.doras}")
        print(f"ura      : {self.uras}")
        print(f"win_tile : {self.players[i_winner].last_got_tile}")
        self.players[i_winner].print_hand()
        print("="*40)


    # UN，REACH(step2)タグ以外の次のタグを読んで，tag_name，attrをメンバ変数にセット
    cpdef void read_next_tag(self) :
        self.i_log += 1
        while True :
            if self.i_log == len(self.xml) : break
            tag_name = self.xml[self.i_log].tag
            attr = self.xml[self.i_log].attrib
            if tag_name != "UN" and tag_name != "BYE" and not(tag_name == "REACH" and attr["step"] == "2") :
                self.tag_name = tag_name
                self.attr = attr
                break
            self.i_log += 1


    # タグを表示
    cpdef void print_tag(self) :
        print("=" * 30)
        print(f"tag_name : {self.tag_name}")
        print(f"attribute : {self.attr}")
        print("=" * 30)


    # ログと食い違いが起こった時の処理
    cpdef void error(self, info) :
        # コンソールに表示
        round_s = ""
        if   self.rounds_num == 0 : round_s = "東"
        elif self.rounds_num == 1 : round_s = "南"
        elif self.rounds_num == 2 : round_s = "西"
        self.is_error = True
        print(colored(info, "red", attrs=["bold"]))
        print("=" * 70)
        print(f"log_id     : {self.log_id}")
        print(f"case       : {round_s}{self.rotations_num+1}局{self.counters_num}本場")
        print(f"deposits   : {self.deposits_num}")
        print(f"tag_name   : {self.tag_name}")
        print(f"attributes : {self.attr}")
        print("")
        for i in range(4) :
            print(f"player{i}\'s hand")
            self.players[i].print_hand()
        print("=" * 70)

        # エラーがあったログを天鳳の牌譜viewerで開くかどうか聞く
        yn = input(colored("Open log viewer?(y/else) : ", "yellow", attrs=["bold"]))
        if yn == "y" : webbrowser.open(f"https://tenhou.net/0/?log={self.log_id}")

        sys.exit()


    # 最終得点の確認
    cpdef void check_final_score(self) :
        print(colored("Check final score", "yellow", attrs=["bold"]))
        print("="*40)
        ten = self.attr["owari"].split(",")
        error = False
        for i in range(4) :
            print(f"players[{i}].score : {self.players[i].score}")
            print(f"xml_log[{i}].score : {int(ten[i*2]) * 100}")
        for i in range(4) :
            if (self.players[i].score != int(ten[i*2]) * 100) and (not(self.is_error)) : self.error("score is different (in TestGame.check_final_score())")
        print("="*40)
        print(colored("OK", "green", attrs=["bold"]))


    # 流局が発生した時にちゃんとRYUUKYOKUタグがセットされているか確認
    cpdef void check_RYUUKYOKU_tag(self) :
        if self.tag_name != "RYUUKYOKU" : self.error("tag is not RYUUKYOKU tag (in TestGame.check_RYUUKYOKU_tag())")
        self.read_next_tag()
