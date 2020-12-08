#std
import random
from typing import List

# 3rd

# ours
from pymod.mytypes import BlockType, TileType
from pymod.yaku import *
from pymod.yakuman import *


class Player :
    def __init__(self, player_num) :
        self.player_num = player_num                      # プレイヤ番号 スタート時の席と番号の関係(0:起家, 1:南家, 2:西家, 3:北家)
        self.score = 25000                                # 点棒

        self.reds = [False] * 3                           # 自分の手の赤があるかどうか，マンピンソウの順, reds[1] is True ==> 手の中に赤5pがある
        self.opened_reds = [False] * 3                    # 自分が晒している手の中に赤があるかどうか
        self.hand = [0] * 38                              # 手牌
        self.opened_hand = [0] * 20
        """
            opened_hand =
            [
                [0+5*n]　フーロの種類（0＝フーロなし、BlockType.*と同期）
                [1+5*n]　そのフーロメンツのうち最も小さい牌番号
                [2+5*n]　そのフーロメンツのうち鳴いた牌の牌番号
                [3+5*n]　その人から相対的に見た、鳴いた他家の番号。1＝下家、2＝対面、3＝上家
                [4*5*n]  副露した直後に切った牌
            ]
        """

        self.discarded_tiles = []                         # 河
        self.discarded_tiles_hist = [0] * 38              # 切られた枚数だけ記録する河
        self.discarded_state = []                         # D:ツモ切り，d:手出し , i:"D" ==> discarded_tiles[i]はツモ切られた牌
        self.furiten_tiles = [0] * 38                     # フリテン牌 furiten_tiles[i] > 0 ==> i番の牌は既に自分で切っているか同巡に切られた牌
        self.same_turn_furiten_tiles = []                 # 同巡に切られた牌

        self.has_stealed = False                          # 1度でもポン, ダイミンカン, チーしていればTrueになる
        self.has_declared_ready = False                   # リーチを宣言しているか
        self.has_declared_double_ready = False            # ダブルリーチを宣言しているか
        self.has_right_to_one_shot = False                # 一発があるか

        self.is_ready = False                             # テンパイか
        self.is_nagashi_mangan = True                     # 流し満貫継続中か

        self.wins = False                                 # 和了ったか

        self.opened_sets_num = 0                          # 晒している面子の数(暗槓含む)
        self.kans_num = 0                                 # 槓した回数

        self.players_wind = 31 + self.player_num          # 自風
        self.last_got_tile = -1                           # 直近でツモった牌 赤牌は番号そのまま(10:赤5筒)

        # アクションフェーズ用
        self.last_discarded_tile = -1                     # 最後に切った牌 赤牌は番号そのまま(10:赤5筒)
        self.exchanged = False
        self.ready = False
        self.anakn = False
        self.kakan = False
        self.kyushu = False

        # 手牌いろいろ計算用
        self.shanten_num_of_kokushi = 13
        self.shanten_num_of_chiitoi = 6
        self.shanten_num_of_normal = 8
        self.shanten_num_of_temp = 0
        self.sets_num = 0
        self.pairs_num = 0
        self.tahtsu_num = 0
        self.hand_composition = [0] * 10                  # 手牌構成
        self.i_hc = 0                                     # 手牌構成計算用インデックス (index of hand composition)

        self.dragons_num = 0
        self.winds_num = 0


    # 局の初期化
    def init_subgame(self, rotations_num:int) -> None :
        self.hand = [0] * 38                              # 手牌
        self.reds = [False] * 3                           # 自分の手に赤があるかどうか，マンピンソウの順．例）reds[1] is True ==> 手の中に赤5pがある
        self.opened_hand = [0] * 20                       # 鳴いている牌
        self.discarded_tiles = []                         # 河
        self.discarded_state = []                         # D:ツモ切り，d:手出し , i:"D" ==> discarded_tiles[i]はツモ切られた牌
        self.furiten_tiles = [0] * 38                     # フリテン牌 furiten_tiles[i] > 0 ==> i番の牌は既に自分で切っているか同巡に切られた牌
        self.same_turn_furiten_tiles = []                 # 同巡に切られた牌

        self.has_stealed = False                          # 1度でもポン, ダイミンカン, チーしていればTrueになる
        self.has_declared_ready = False                   # リーチを宣言しているか
        self.has_declared_double_ready = False            # ダブルリーチを宣言しているか
        self.has_right_to_one_shot = False                # 一発があるか

        self.is_ready = False                             # テンパイか
        self.is_nagashi_mangan = True                     # 流し満貫か

        self.wins = False                                 # 和了ったか

        self.opened_sets_num = 0                          # 晒している面子の数(暗槓含む)
        self.kans_num = 0                                 # 槓した回数

        self.players_wind = 31 + (((self.player_num+4) - rotations_num)%4)
        self.last_got_tile = -1                           # 直近でツモった牌 赤牌は番号そのまま(10:赤5筒)
        self.last_discarded_tile = -1                     # 最後に切った牌 赤牌は番号そのまま(10:赤5筒)

        self.shanten_num_of_kokushi = 13
        self.shanten_num_of_chiitoi = 6
        self.shanten_num_of_normal = 8
        self.shanten_num_of_temp = 0
        self.sets_num = 0
        self.pairs_num = 0
        self.tahtsu_num = 0                               # 英語見つからなくて草
        self.composition_of_hand = [0] * 10               # 手牌構成
        self.i_hc = 0                                     # 手牌構成計算用インデックス （index of hand composition)

        # パオ判定用
        self.dragons_num = 0
        self.winds_num = 0


    # 国士無双の向聴数を返す
    def calc_shanten_num_of_kokushi(self, tile:int = -1) -> int :
        hand = self.hand[:]

        if tile > -1 :
            if tile in TileType.REDS :
                tile += 5
            hand[tile] += 1

        pairs_num = 0
        shanten_num = 13

        for i in (TileType.TERMINALS | TileType.HONORS) :
            if hand[i] != 0 : shanten_num -= 1
            if hand[i] > 1 and pairs_num == 0 : pairs_num = 1

        shanten_num -= pairs_num
        self.shanten_num_of_kokushi = shanten_num

        return shanten_num


    # 国士無双の有効牌のリストを返す
    def effective_tiles_of_kokushi(self) -> list :
        hand = self.hand[:]
        effective_tiles = [0] * 38

        shanten_num = self.calc_shanten_num_of_kokushi()
        for i in (TileType.TERMINALS | TileType.HONORS) :
            if self.calc_shanten_num_of_kokushi(i) < shanten_num : effective_tiles[i] = 1

        return effective_tiles


    # 七対子の向聴数を返す
    def calc_shanten_num_of_chiitoi(self, tile:int = -1) -> int :
        hand = self.hand[:]

        if tile > -1 :
            if tile in TileType.REDS : tile += 5
            hand[tile] += 1

        shanten_num = 6
        kind = 0 # 6対子あっても孤立牌がないと聴牌にならないのでそれのチェック用
        for i in range(1,38) :
            if hand[i] >= 1 :
                kind += 1
            if hand[i] >= 2 :
                shanten_num -= 1
        if kind < 7 :
            shanten_num += 7 - kind

        self.shanten_num_of_chiitoi = shanten_num

        return shanten_num


    # 七対子の有効牌のリストを返す
    def effective_tiles_of_chiitoi(self) -> list :
        effective_tiles = [0] * 38
        shanten_num = self.calc_shanten_num_of_chiitoi()
        for i in range(38) :
            if i % 10 == 0 : continue
            if self.calc_shanten_num_of_chiitoi(i) < shanten_num : effective_tiles[i] = 1

        return effective_tiles


    # 通常手の向聴数を返す
    def calc_shanten_num_of_normal(self, tile:int = -1) -> int :
        hand = self.hand[:]
        self.shanten_num_of_normal = 8
        self.sets_num = self.opened_sets_num
        self.pairs_num = 0
        self.tahtsu_num = 0

        if tile > -1 :
            if tile in TileType.REDS : tile += 5
            hand[tile] += 1

        for i in range(1,38) :
            if hand[i] >= 2 :
                self.pairs_num += 1
                hand[i] -= 2
                self.pick_out_mentsu(1, hand)
                hand[i] += 2
                self.pairs_num -= 1
        self.pick_out_mentsu(1, hand)

        return self.shanten_num_of_normal


    # 面子を抜き出す
    def pick_out_mentsu(self, i:int , hand:List[int]) -> None :
        while i < 38 and hand[i] == 0 : i += 1
        if i > 37 :
            self.pick_out_tahtsu(1, hand)
            return
        if hand[i] > 2 :
            self.sets_num += 1
            hand[i] -= 3
            self.pick_out_mentsu(i, hand)
            hand[i] += 3
            self.sets_num -= 1
        if  i < 28 and hand[i+1] > 0 and hand[i+2] > 0 :
            self.sets_num += 1
            hand[i] -= 1
            hand[i+1] -= 1
            hand[i+2] -= 1
            self.pick_out_mentsu(i, hand)
            hand[i] += 1
            hand[i+1] += 1
            hand[i+2] += 1
            self.sets_num -= 1
        self.pick_out_mentsu(i+1, hand)


    # 塔子を抜き出
    def pick_out_tahtsu(self, i:int, hand:List[int]) -> None :
        while i < 38 and hand[i] == 0 : i += 1
        if i > 37 :
            self.shanten_num_of_temp = 8 - self.sets_num * 2 - self.tahtsu_num - self.pairs_num
            if self.shanten_num_of_temp < self.shanten_num_of_normal :
                self.shanten_num_of_normal = self.shanten_num_of_temp
            return
        if self.sets_num + self.tahtsu_num < 4 :
            if hand[i] == 2 :
                self.tahtsu_num += 1
                hand[i] -= 2
                self.pick_out_tahtsu(i, hand)
                hand[i] += 2
                self.tahtsu_num -= 1
            if i < 29 and hand[i+1] != 0 :
                self.tahtsu_num += 1
                hand[i] -= 1
                hand[i+1] -= 1
                self.pick_out_tahtsu(i, hand)
                hand[i] += 1
                hand[i+1] += 1
                self.tahtsu_num -= 1
            if i < 29 and i % 10 < 9 and hand[i+2] != 0 :
                self.tahtsu_num += 1
                hand[i] -= 1
                hand[i+2] -= 1
                self.pick_out_tahtsu(i, hand)
                hand[i] += 1
                hand[i+2] += 1
                self.tahtsu_num -= 1
        self.pick_out_tahtsu(i+1, hand)


    # 通常手の有効牌のリストを返す
    def effective_tiles_of_normal(self) -> list :
        effective_tiles = [0] * 38
        not_alone_tiles = self.is_not_alone_tiles()
        shanten_num = self.calc_shanten_num_of_normal()

        for i in range(1, 38) :
            if not_alone_tiles[i] == 0 : continue
            if self.calc_shanten_num_of_normal(i) < shanten_num : effective_tiles[i] = 1
        return effective_tiles


    # ある牌を引いた時孤立牌になるかどうかの情報が入ったリストを返す
    ## i番の牌を引いた時に孤立牌になる　　 : not_alone_tiles[i] = 0
    ## i番の牌を引いた時に孤立牌にならない : not_alone_tiles[i] = 1
    def is_not_alone_tiles(self) -> list :
        not_alone_tiles = [0] * 38

        for i in range(1, 38) :
            if self.hand[i] == 0 : continue
            if i < 30 :
                if i % 10 == 1 :
                    not_alone_tiles[i:i+3] = [1] * 3
                elif i % 10 == 2 :
                    not_alone_tiles[i-1:i+3] = [1] * 4
                elif i % 10 >= 3 and i % 10 <= 7 :
                    not_alone_tiles[i-2:i+3] = [1] * 5
                elif i % 10 == 8 :
                    not_alone_tiles[i-2:i+2] = [1] * 4
                elif i % 10 == 9 :
                    not_alone_tiles[i-2:i+1] = [1] * 3
            elif i > 30 : not_alone_tiles[i] = 1

        return not_alone_tiles


    # 点棒の授受
    def score_points(self, points:int) -> None :
        self.score += points


    # 立直宣言
    def declare_ready(self, is_first_turn:bool) -> None :
        if is_first_turn : self.has_declared_double_ready = True
        else : self.has_declared_ready = True
        self.has_right_to_one_shot = True
        self.score -= 1000


    # 牌を手牌に加える．配牌取得，ツモ，ロンで使う．
    def get_tile(self, tile:int) -> None :
        self.last_got_tile = tile
        if tile in TileType.REDS :
            self.reds[tile//10] = True
            tile += 5
        self.hand[tile] += 1


    # 牌を捨てる
    def discard_tile(self, game, players) -> int :
        discarded_tile, exchanged = game.action.decide_which_tile_to_discard(game, players, self.player_num)
        self.last_discarded_tile = discarded_tile

        # 河への記録
        self.discarded_state += [self.exchanged]
        self.discarded_tiles += [discarded_tile]

        # 赤牌を番号に変換
        if discarded_tile in TileType.REDS :
            self.reds[discarded_tile // 10] = False
            discarded_tile += 5

        # 手牌から切る牌を減らす
        self.hand[discarded_tile] -= 1
        # 切る牌をフリテン牌に記録する
        self.furiten_tiles[discarded_tile] += 1
        # 枚数だけ記録する河に切る牌を記録する
        self.discarded_tiles_hist[discarded_tile] += 1

        return self.last_discarded_tile


    # 聴牌かどうかを判定
    def check_hand_is_ready(self) -> bool :
        if (self.calc_shanten_num_of_normal() == 0) and self.has_used_up_winning_tile() or \
           self.calc_shanten_num_of_chiitoi() == 0 or \
           self.calc_shanten_num_of_kokushi() == 0 : self.is_ready = True
        else : self.is_ready = False

        return self.is_ready


    # 和了牌を使い切っているかどうか
    # 天鳳の処理はこうなってるはず
    # 天鳳では3pを加カンしている状態で嵌3p待ちでもテンパイ扱いだったし，2015年のデータによるテストでは点数に誤差がでていない
    # (きっとおかしいんだけどね)
    def has_used_up_winning_tile(self) -> bool :
        effective_tiles = self.effective_tiles_of_normal()
        num_of_winning_tile = 0
        for i in range(38) :
            if effective_tiles[i] == 0 : continue
            num_of_winning_tile += 4
            num_of_winning_tile -= hand[i]
        if num_of_winning_tile == 0 : return False
        return True


    # 流し満貫かチェック
    def check_player_is_nagashi_mangan(self) -> bool :
        if self.last_discarded_tile in (TileType.TERMINALS | TileType.HONORS): self.is_nagashi_mangan = True
        else : self.is_nagashi_mangan = False

        return self.is_nagashi_mangan


    # フリテン牌を追加
    def add_furiten_tile(self, tile:int) -> None : self.furiten_tiles[tile] += 1


    # 同巡フリテン牌を追加
    def add_same_turn_furiten_tile(self, tile:int) -> None :
        self.same_turn_furiten_tiles += [tile]
        self.furiten_tiles[tile] += 1


    # 同巡フリテンを解消
    def reset_same_turn_furiten(self) -> None :
        for i in self.same_turn_furiten_tiles : self.furiten_tiles[i] -= 1
        self.same_turn_furiten_tiles = []


    # 鳴いて晒した牌を全部戻した手をreturnする
    def put_back_opened_hand(self) -> List[int] :
        hand = self.hand[:]
        for i in range(0,20,5) :
            if self.opened_hand[i] == 0 : break
            elif self.opened_hand[i] == BlockType.OPENED_TRIPLET : hand[self.opened_hand[i+1]] += 3
            elif self.opened_hand[i] == BlockType.OPENED_RUN :
                n = self.opened_hand[i+1]
                hand[n] += 1
                hand[n+1] += 1
                hand[n+2] += 1
            else : hand[self.opened_hand[i+1]] += 4
        return hand


    # 和了するかどうかの判定
    def decide_win(self, game:"Game", ron_tile:int = -1) -> bool :
        # そもそも和了れるかどうかの判定
        # TODO ここじゃなくてgame.pyの中でやった方がいい気がするよね...
        if not(self.can_win(game, ron_tile)) : return False

        # TODO 和了るかどうかの判断　今は和了れたら和了るようにしている
        self.wins = True

        return self.wins


    # ポン or 大明槓するかどうかの判断
    def decide_pon_or_kan(self, game:"Game", players:List["Player"], tile:int) -> (bool, bool) :
        red = False
        if tile in TileType.REDS :
            tile += 5
            red = True

        # そもそもポン or 大明槓できるかの判定
        if self.hand[tile] < 2 : return False, False

        # TODO ポンするかどうかの判断　今は鳴かないようにしている
        pon = False
        kan = False

        return pon, kan


    # チーするかどうかの判断
    def decide_chii(self, game:"Game", players:List["Player"], tile:int) -> (bool, int, int) :
        if tile in TileType.REDS : tile += 5

        # チーできるかどうかの判定
        if self.can_chii(tile) is False : return False, -1, -1

        ### TODO チーするかどうかの判断
        ### chii_action:0 => スルー
        ### chii_action:1 => 下チー
        ### chii_action:2 => 嵌張チー
        ### chii_action:3 => 上チー
        ### がNNから帰ってくるようにしたい

        # 返り値の処理
        chii = False
        chii_action = 0 ### TODO 今はチーできないようにしている

        if chii_action == 0 : tile1, tile2 = -1, -1
        elif chii_action == 1 : chii, tile1, tile2 = True, (tile - 2), (tile - 1)
        elif chii_action == 2 : tile1, tile2 = True, (tile-1), (tile + 1)
        elif chii_action == 3 : tile1, tile2 = True, (tile+1), (tile + 2)
        else : tile1, tile2 = -1, -1 # 想定しない処理　一応

        ### TODO 赤含みでチーできる時はチーするようにしているが本当は選択できる方が望ましい
        if tile1 in TileType.FIVES and self.reds[tile1//10] : tile1 -= 5
        elif tile2 in TileType.FIVES and self.reds[tile2//10] : tile2 -= 5

        return chii, tile1, tile2


    # チーできるかどうか
    def can_chii(self, tile) -> bool :
        # 字牌はチーできない
        if tile > 30 : return False

        # 判定．順に下チー，嵌張チー，上チーの判定をorで繋いでる
        can_chii = False
        if (tile % 10 >= 3 and self.hand[tile-2] > 0 and self.hand[tile-1] > 0) or \
           (tile % 10 >= 2 and tile % 10 <= 8 and self.hand[tile-1] > 0 and self.hand[tile+1] > 0) or \
           (tile % 10 >= 3 and self.hand[tile-2] > 0 and self.hand[tile-1] > 0) : can_chii = True

        return can_chii


    # 和了れるかどうか
    def can_win(self, game: "Game", ron_tile: int = -1) -> bool :
        ron, is_chiitoi, is_kokushi, is_normal = False, False, False, False

        # 向聴数的に和了っているかどうか確認
        if self.calc_shanten_num_of_normal(ron_tile) == -1 : is_normal = True
        elif self.calc_shanten_num_of_chiitoi(ron_tile) == -1 : is_chiitoi = True
        elif self.calc_shanten_num_of_kokushi(ron_tile) == -1 : is_kokushi = True
        if not(is_chiitoi or is_kokushi or is_normal) : return False

        # ロンの時の処理
        if ron_tile > -1 :
            ron = True
            if self.is_furiten(is_chiitoi, is_kokushi, is_normal, ron_tile) : return False # フリテンだったら和了れない

        # 役があるかどうかをチェック
        if is_chiitoi or is_kokushi : return True
        if is_normal and self.has_yaku(game, ron, ron_tile) : return True

        return False


    # フリテンかどうか
    def is_furiten(self, is_chiitoi:bool, is_kokushi:bool, is_normal:bool, ron_tile:int) -> bool :
        if ron_tile in TileType.REDS : ron_tile += 5
        hand = self.hand[:]
        if is_normal :
            effective_tiles = self.effective_tiles_of_normal()
            for i in range(1, 38) :
                if i % 10 == 0 : continue
                if self.furiten_tiles[i] > 0 and effective_tiles[i] > 0 : return True
        elif is_chiitoi :
            if self.furiten_tiles[ron_tile] > 0 : return True
        elif is_kokushi :
            effective_tiles = self.effective_tiles_of_kokushi()
            for i in (TileType.TERMINALS | TileType.HONORS) :
                if self.furiten_tiles[i] > 0 and effective_tiles[i] > 0 : return True

        return False


    # 役があるか．和了れるかどうかの判定に使うから全部の役は見ない．
    def has_yaku(self, game:"Game", ron:bool, ron_tile:int) -> bool:
        if ron_tile in TileType.REDS : ron_tile += 5
        if self.has_declared_ready : return True
        if self.has_declared_double_ready : return True
        hand = self.put_back_opened_hand()
        if all_simples(hand) : return True
        if white_dragon(hand) : return True
        if green_dragon(hand) : return True
        if red_dragon(hand) : return True
        if prevailing_wind(hand, game.prevailing_wind) : return True
        if players_wind(hand, self.players_wind) : return True
        if not(ron) and not(self.has_stealed) : return True
        if half_flush(hand) : return True
        if flush(hand) : return True
        if game.is_last_tile() : return True # 海底・河底
        if game.rinshan_draw_flag : return True # 嶺上
        if game.dora_opens_flag : return True # 槍槓
        if self.has_yaku_based_on_tiles(game.prevailing_wind, self.players_wind, ron, ron_tile) : return True

        return False


    # 手牌構成による役があるか．和了れるかどうかの判定に使うから全部の役は見ない．
    def has_yaku_based_on_tiles(self, prevailing_wind:int, ron:bool, ron_tile:int) -> bool :
        hand = self.hand[:]
        if ron : hand[ron_tile] += 1
        self.hand_composition = [0] * 10
        self.i_hc = 0

        #副露メンツ確定
        for i in range(0,4) :
            if self.opened_hand[i*5] != 0 :
                self.hand_composition[(i*2)] = self.opened_hand[i*5]
                self.hand_composition[(i*2)+1] = self.opened_hand[(i*5)+1]
                self.i_hc += 2
            else : break

        #頭抜き出し
        for i in range(1,38) :
            if hand[i] == 0 : continue
            if hand[i] >= 2 :
                hand[i] = hand[i] - 2
                self.hand_composition[self.i_hc] = BlockType.PAIR
                self.hand_composition[self.i_hc+1] = i
                self.i_hc += 2
                there_is_yaku = self.pick_out_mentsu_for_composition_hand(hand, prevailing_wind, self.players_wind, ron, ron_tile);
                if there_is_yaku : return True
                self.i_hc -= 2
                self.hand_composition[self.i_hc] = 0
                self.hand_composition[self.i_hc+1] = 0
                hand[i] = hand[i] + 2

        return False


    # 面子を抜き出す．_pick_out_mentsu()と違い高速化のため役判定に不要な処理を省いたバージョン．
    def pick_out_mentsu2(self, hand:List[int], prevailing_wind:int, ron:bool, ron_tile:int) -> bool :
        for i in range(1,38) :

            # 判定する手牌構成が決まったら役があるかどか判定結果を返す
            if self.hand_composition[9] != 0 :
                if no_points_hand(self.hand_composition, ron_tile, prevailing_wind, self.players_wind) : return True
                if one_set_of_identical_sequences(self.hand_composition) : return True
                if terminal_or_honor_in_each_set(self.hand_composition) : return True
                if three_color_straight(self.hand_composition) : return True
                if straight(self.hand_composition) : return True
                if all_triplet_hand(self.hand_composition) : return True
                if three_color_triplets(self.hand_composition) : return True
                if three_kans(self.hand_composition) : return True
                if three_closed_triplets(self.hand_composition) : return True
                if terminal_in_each_set(self.hand_composition) : return True
                return False

            # インデックスが指す場所に牌がなければ次の牌を見にいく
            if hand[i] == 0 : continue

            # 暗刻抜き出し
            if hand[i] >= 3 :
                hand[i] -= 3
                if i == ron_tile and ron and hand[i] == 0 : self.hand_composition[self.i_hc] = BlockType.OPENED_TRIPLET
                else : self.hand_composition[self.i_hc] = BlockType.CLOSED_TRIPLET
                self.hand_composition[self.i_hc+1] = i
                self.i_hc += 2
                self.pick_out_mentsu2(hand, prevailing_wind, self.players_wind, ron, ron_tile)
                self.i_hc -= 2
                self.hand_composition[self.i_hc] = 0
                self.hand_composition[self.i_hc+1] = 0
                hand[i] += 3

            # 順子抜き出し
            if i < 30 and hand[i] != 0 and hand[i+1] != 0 and hand[i+2] != 0 :
                hand[i] = hand[i] - 1
                hand[i+1] = hand[i+1] - 1
                hand[i+2] = hand[i+2] - 1
                self.hand_composition[self.i_hc] = BlockType.CLOSED_RUN
                self.hand_composition[self.i_hc+1] = i
                self.i_hc += 2
                self.pick_out_mentsu2(hand, prevailing_wind, self.players_wind, ron, ron_tile)
                self.i_hc -= 2
                self.hand_composition[self.i_hc+1] = 0
                self.hand_composition[self.i_hc] = 0
                hand[i] += 1
                hand[i+1] += 1
                hand[i+2] += 1


    # 暗槓の処理
    def proc_ankan(self, tile:int) -> None :
        self.kans_num += 1
        self.opened_sets_num += 1
        self.opened_hand[self.opened_sets_num * 5] = BlockType.CLOSED_KAN
        self.opened_hand[self.opened_sets_num * 5 + 1] = tile
        self.opened_hand[self.opened_sets_num * 5 + 2] = tile
        self.opened_hand[self.opened_sets_num * 5 + 3] = 0
        self.hand[tile] -= 4
        if tile in TileType.FIVES :
            self.reds[tile//10] = False
            self.opened_reds[tile//10] = True


    # 加槓の処理
    def proc_kakan(self, tile:int) -> int :
        self.kans_num += 1
        for i in range(4) :
            if self.opened_hand[i*5] == BlockType.OPENED_TRIPLET and self.opened_hand[(i*5)+1] == tile :
                self.opened_hand[i*5] = BlockType.OPENED_KAN
                self.hand[tile] -= 1
                if tile in TileType.FIVES and self.reds[tile//10]:
                    self.reds[tile//10]= False
                    self.opened_reds[tile//10] = True

                # ポンした相手の位置の情報がloggingに必要なので渡す
                return (self.opened_hand[(i*5)+3], self.opened_reds[tile//10])


    # 大明槓の処理
    def proc_daiminkan(self, tile:int, pos:int) -> None :
        if tile in TileType.REDS :
            self.opened_reds[tile//10] = True
            tile += 5
        elif tile in TileType.FIVES and self.reds[tile//10]:
            self.reds[tile//10]= False
            self.opened_reds[tile//10] = True

        self.kans_num += 1
        self.opened_sets_num += 1
        self.has_stealed = True
        self.opened_hand[(self.opened_sets_num * 5) + 0] = BlockType.OPENED_KAN
        self.opened_hand[(self.opened_sets_num * 5) + 1] = tile
        self.opened_hand[(self.opened_sets_num * 5) + 2] = tile
        self.opened_hand[(self.opened_sets_num * 5) + 3] = pos
        self.hand[tile] -= 3


    # ポンの処理
    def proc_pon(self, tile:int, pos:int) -> int :
        if tile in TileType.REDS :
            self.opened_reds[tile//10] = True
            tile += 5
        elif tile in TileType.FIVES and self.reds[tile//10]:
            self.reds[tile//10]= False
            self.opened_reds[tile//10] = True

        self.opened_sets_num += 1
        self.has_stealed = True
        self.opened_hand[(self.opened_sets_num * 5) + 0] = BlockType.OPENED_TRIPLET
        self.opened_hand[(self.opened_sets_num * 5) + 1] = tile
        self.opened_hand[(self.opened_sets_num * 5) + 2] = tile
        self.opened_hand[(self.opened_sets_num * 5) + 3] = pos
        self.hand[tile] -= 2

        if tile in TileType.DRAGONS :
            self.dragons_num += 1
            if self.dragons_num == 3 : return 0 # 大三元のパオであれば0を返す
        elif tile in TileType.HONORS :
            self.winds_num += 1
            if self.winds_num == 4 : return 1 # 大喜四のパオであれば1を返す

        return -1 # パオでなければ-1を返す


    # チーの処理
    def proc_chii(self, tile:int, tile1:int, tile2:int) -> None :
        if tile in TileType.REDS :
            self.opened_reds[tile//10] = True
            tile += 5
        elif tile1 in TileType.REDS :
            self.reds[tile1//10] = False
            self.opened_reds[tile1//10] = True
            tile1 += 5
        elif tile2 in TileType.REDS :
            self.reds[tile2//10] = False
            self.opened_reds[tile2//10] = True
            tile2 += 5

        self.opened_sets_num += 1
        self.has_stealed = True
        self.opened_hand[(self.opened_sets_num * 5) + 0] = BlockType.OPENED_RUN
        if tile1 > tile : min_tile = tile
        else : min_tile = tile1
        self.opened_hand[(self.opened_sets_num * 5) + 1] = min_tile
        self.opened_hand[(self.opened_sets_num * 5) + 2] = tile
        self.opened_hand[(self.opened_sets_num * 5) + 3] = 3
        self.hand[tile1] -= 1
        self.hand[tile2] -= 1


    # 鳴いた後の手出し牌を登録
    def add_tile_player_discard_after_displaying(self, tile:int) -> None :
        self.opened_hand[((self.opened_sets_num - 1) * 5) + 4] = tile


    # 加槓できるかどうか判定
    # TODO ちゃんと書く
    def can_kakan(self, game:"Game") -> List[int] :
        return []


    # 暗槓できるかどうか判定，できる場合は暗槓できる牌の牌番号のリストを返す
    def can_ankan(self, game:"Game") -> List[int] :
        can_ankan_tiles = []

        # 手牌の中に暗槓できる牌があったらcan_ankan_tilesに牌番号を追加
        for i in range(1,38) :
            if self.hand[i] == 4 : can_ankan_tiles.append(i)

        # 暗槓できる牌が無かったら空listをreturn
        if not(can_ankan_tiles) : return can_ankan_tiles

        # ルール上槓できるかをチェック
        opened_doras_num = 0
        for state in game.dora_has_opened :
            if state : opened_doras_num += 1
        #
        if opened_doras_num == 5 : return []

        return can_ankan_tiles


    # 槓しない or どの牌で槓するか決める
    def decide_which_tile_to_kan(self, game:"Game", playes:List["Player"]) -> int :
        ### 今は強制的に槓しないようにする
        ### NNの計算とかが入る
        return -1


    # 槓するかどうか決める
    def decide_to_kan(self, game:"Game", players:List["Player"]) -> (int, bool, bool):
        tile, ankan, kakan = -1, False, False

        # 槓できるか判定
        can_ankan_tiles = self.can_ankan(game)
        can_kakan_tiles = self.can_kakan(game)

        # プレイヤが槓の内容（どの牌で槓するか，しないか）を決める
        tile = self.decide_which_tile_to_kan(game, players)
        if tile in can_ankan_tiles : ankan = True
        elif tile in can_kakan_tiles : kakan = True
        else : tile = -1 # decide_which_tile_to_kan()でとんでもないものが帰ってきたときにバグらないように一応制御

        return tile, ankan, kakan


    # 立直宣言するかどうか決める
    # TODO リーチ判断．ちゃんと書く
    def decide_to_declare_ready(self, tile) -> bool :
        return False


    # 九種九牌を宣言するかどうか決める
    def decide_to_declare_nine_orphans(self) -> bool :

        # 九種九牌をそもそも宣言できるかどうかの判定
        terminals_num = 0
        for i in (TileType.TERMINALS | TileType.HONORS) :
            if self.hand[i] > 0 :
                terminals_num += 1

        # 今はとりあえず流局できたらするようにする
        # TODO ちゃんと判断するように変更
        if terminals_num > 8 : return True

        return False


    # 切る牌を決める
    # TODO 今は強制ツモ切り．ちゃんと書く．
    def decide_which_tile_to_discard(self) :
        self.last_discarded_tile = self.last_got_tile
        return (self.last_got_tile, False)


    # アクションフェーズでのアクションを決める
    def decide_action(self, game:"Game", players:List["Player"]) -> (int, bool, bool, bool, bool, bool):
        # プレイヤの行動決定，tile:赤は(0,10,20)表示
        tile, exchanged, ready, ankan, kakan, kyushu = -1, False, False, False, False, False

        # 槓するかどうか決める
        tile, ankan, kakan = self.decide_to_kan(game, players)
        if ankan or kakan : return tile, exchanged, ready, ankan, kakan, kyushu

        # 立直するかどうか決める
        ready = self.decide_to_declare_ready(tile)

        # 九種九牌で流局するかどうか決める
        if game.is_first_turn : kyusyu = self.decide_to_declare_nine_orphans()
        else : kyusyu = False

        # return tile, exchanged, ready, ankan, kakan, kyushu
        return tile, False, False, False, False, False


    # handを標準出力に表示
    def print_hand(self) -> None:
        s_hand = ""
        for i in range(1,38) :
            if i == 10 : s_hand += "m"
            elif i == 20 : s_hand += "p"
            elif i == 30 : s_hand += "s"
            for j in range(self.hand[i]) :
                if i < 30 : s_hand += str(i%10)
                elif i == 31 : s_hand += "東"
                elif i == 32 : s_hand += "南"
                elif i == 33 : s_hand += "西"
                elif i == 34 : s_hand += "北"
                elif i == 35 : s_hand += "白"
                elif i == 36 : s_hand += "発"
                else : s_hand += "中"
        print(s_hand)
