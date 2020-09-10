#std
import random
from typing import List

# 3rd

# ours
from game import Game
from block import Block
from tile_type import TileType


"""
ツモ切りのDとd逆にしたい
"""


class Player :


    def __init__(self, player_num) :

        self.player_num = i                               # プレイヤ番号 スタート時の席と番号の関係(0:起家, 1:南家, 2:西家, 3:北家)
        self.score = 25000                                # 点棒

        self.hand = [0] * 38                              # 手牌
        self.reds = [False] * 3                           # 自分の手の赤があるかどうか，マンピンソウの順, reds[1] is True ==> 手の中に赤5pがある
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

        self.players_wind = 31 + self.player_num          # 自風
        self.last_tile_drawn = -1                         # 直近でツモった牌 赤牌は番号そのまま(10:赤5筒)
        self.last_tile_discarded = -1                     # 最後に切った牌 赤牌は番号そのまま(10:赤5筒)

        # 手牌いろいろ計算用
        self.syanten_num_of_kokushi = 13
        self.syanten_num_of_chiitoi = 6
        self.syanten_num_of_normal = 8
        self.syanten_num_of_temp = 0
        self.sets_num = 0
        self.pairs_num = 0
        self.tahtsu_num = 0                               # 英語見つからなくて草
        self.composition_of_hand = [0] * 10               # 手牌構成
        self.i_composition_of_hand = 0                    # 手牌構成計算用インデックス

        # ログ用
        self.actions = []
        self.starting_hand = []
        self.tiles_player_drew = []


    def init_subgame(self, rotations_num: int) -> None :

        self.hand = [0] * 38                              # 手牌
        self.reds = [False] * 3                           # 自分の手の赤があるかどうか，マンピンソウの順, reds[1] is True ==> 手の中に赤5pがある
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
        self.last_tile_drawn = -1                         # 直近でツモった牌 赤牌は番号そのまま(10:赤5筒)
        self.last_tile_discarded = -1                     # 最後に切った牌 赤牌は番号そのまま(10:赤5筒)

        # 手牌いろいろ計算用
        self.syanten_num_of_kokushi = 13
        self.syanten_num_of_chiitoi = 6
        self.syanten_num_of_normal = 8
        self.syanten_num_of_temp = 0
        self.sets_num = 0
        self.pairs_num = 0
        self.tahtsu_num = 0                               # 英語見つからなくて草
        self.composition_of_hand = [0] * 10               # 手牌構成
        self.i_composition_of_hand = 0                    # 手牌構成計算用インデックス

        # ログ用
        self.actions = []
        self.starting_hand = []
        self.tiles_player_drew = []

        # self.hand = [0] * 38
        # self.opened_hand = [0] * 20
        # self.has_stealed = False
        # self.opened_sets_num = 0
        # self.discarded_tiles = []
        # self.discarded_state = []
        # self.furiten_tiles = [0] * 38
        # self.round_furiten_tiles = []
        # self.red = [False] * 3
        # self.tsumo = -1
        # self.action = [-1, False, False, False, False]
        # self.riichi = False
        # self.d_riichi = False
        # self.ready = True
        # self.ippatsu = False
        # self.win = False
        # self.all_discarded_tiles_are_edge_tiles = True
        # self.num_of_dragon = 0
        # self.num_of_winds = 0
        # self.num_of_kan = 0
        # self.syanten_num_of_kokushi = 13
        # self.syanten_num_of_chiitoi = 6
        # self.syanten_num_of_normal = 8
        # self.syanten_num_of_temp = 0
        # self.n_mentsu = 0
        # self.n_pair = 0
        # self.n_taatsu = 0
        # self.composition_of_hand = [0] * 10
        # self.p_composition_of_hand = 0
        # self.behavior = []
        # self.first_hand = []
        # self.tsumo_tiles = []


    def calc_syanten_num_of_kokushi(self, int ron_tile = -1) : #国士無双のシャンテン数を返す
        def int[38] hand = self.hand
        def int i, pair, syanten_num

        if ron_tile > -1 :
            if ron_tile in [0,10,20] : ron_tile += 5
            hand[ron_tile] += 1
        pair = 0
        syanten_num = 13
        for i in [1,9,11,19,21,29,31,32,33,34,35,36,37] :
            if hand[i] != 0 : syanten_num -= 1
            if hand[i] > 1 and pair == 0 : pair = 1
        syanten_num -= pair
        self.syanten_num_of_kokushi = syanten_num
        ###print("syanten_num : %d" % syanten_num)
        return syanten_num

    def list effective_tiles_of_kokushi(self) :
        def int[38] hand = self.hand
        def int[38] effective_tiles = [0] * 38
        def int i, n_syanten
        ###print(effective_tiles)
        n_syanten = self.calc_syanten_num_of_kokushi()
        for i in [1,9,11,19,21,29,31,32,33,34,35,36,37] :
            if self.calc_syanten_num_of_kokushi(i) < n_syanten : effective_tiles[i] = 1
        return effective_tiles

    def int calc_syanten_num_of_chiitoi(self, int ron_tile = -1) : #七対子のシャンテン数を返す
        def int[38] hand = self.hand
        def int i, syanten_num ,kind
        if ron_tile > -1 :
            if ron_tile in [0,10,20] : ron_tile += 5
            hand[ron_tile] += 1
        syanten_num = 6
        kind = 0
        for i in range(1,38) :
            if hand[i] >= 1 :
                kind += 1
            if hand[i] >= 2 :
                syanten_num -= 1
        if kind < 7 :
            syanten_num += 7 - kind
        self.syanten_num_of_chiitoi = syanten_num
        return syanten_num

    def list effective_tiles_of_chiitoi(self) :
        def int[38] effective_tiles = [0] * 38
        def int i, n_syanten
        n_syanten = self.calc_syanten_num_of_chiitoi()
        for i in range(38) :
            if i % 10 == 0 : continue
            if self.calc_syanten_num_of_chiitoi(i) < n_syanten : effective_tiles[i] = 1
        return effective_tiles

    def int calc_syanten_num_of_normal(self, int ron_tile = -1) :
        self.syanten_num_of_normal = 8
        self.n_mentsu = self.displayed_num
        self.n_pair = 0
        self.n_taatsu = 0
        def int i
        def int[38] hand = self.hand
        if ron_tile > -1 :
            if ron_tile in [0,10,20] : ron_tile += 5
            hand[ron_tile] += 1
        for i in range(1,38) :
            if hand[i] >= 2 :
                self.n_pair += 1
                hand[i] -= 2
                self._pick_out_mentsu(1, hand)
                hand[i] += 2
                self.n_pair -= 1
        self._pick_out_mentsu(1, hand)
        ###print("syanten_num : %d" % self.syanten_num_of_normal)
        return self.syanten_num_of_normal

    def void _pick_out_mentsu(self, int i, int[:] hand) :
        while i < 38 and hand[i] == 0 : i += 1
        if i > 37 :
            self._pick_out_taatsu(1, hand)
            return
        if hand[i] > 2 :
            self.n_mentsu += 1
            hand[i] -= 3
            self._pick_out_mentsu(i, hand)
            hand[i] += 3
            self.n_mentsu -= 1
        if  i < 28 and hand[i+1] > 0 and hand[i+2] > 0 :
            self.n_mentsu += 1
            hand[i] -= 1
            hand[i+1] -= 1
            hand[i+2] -= 1
            self._pick_out_mentsu(i, hand)
            hand[i] += 1
            hand[i+1] += 1
            hand[i+2] += 1
            self.n_mentsu -= 1
        self._pick_out_mentsu(i+1, hand)

    def void _pick_out_taatsu(self, int i, int[:] hand) :
        while i < 38 and hand[i] == 0 : i += 1
        if i > 37 :
            self.syanten_num_of_temp = 8 - self.n_mentsu * 2 - self.n_taatsu - self.n_pair
            if self.syanten_num_of_temp < self.syanten_num_of_normal :
                self.syanten_num_of_normal = self.syanten_num_of_temp
            return
        if self.n_mentsu + self.n_taatsu < 4 :
            if hand[i] == 2 :
                self.n_taatsu += 1
                hand[i] -= 2
                self._pick_out_taatsu(i, hand)
                hand[i] += 2
                self.n_taatsu -= 1
            if i < 29 and hand[i+1] != 0 :
                self.n_taatsu += 1
                hand[i] -= 1
                hand[i+1] -= 1
                self._pick_out_taatsu(i, hand)
                hand[i] += 1
                hand[i+1] += 1
                self.n_taatsu -= 1
            if i < 29 and i % 10 < 9 and hand[i+2] != 0 :
                self.n_taatsu += 1
                hand[i] -= 1
                hand[i+2] -= 1
                self._pick_out_taatsu(i, hand)
                hand[i] += 1
                hand[i+2] += 1
                self.n_taatsu -= 1
        self._pick_out_taatsu(i+1, hand)

    def list effective_tiles_of_normal(self) :
        def int[38] not_alone_tiles, effective_tiles
        def int n_syanten, i
        effective_tiles = [0] * 38
        not_alone_tiles = self._is_not_alone_tiles()
        n_syanten = self.calc_syanten_num_of_normal()
        for i in range(1, 38) :
            if not_alone_tiles[i] == 0 : continue
            if self.calc_syanten_num_of_normal(i) < n_syanten : effective_tiles[i] = 1
        return effective_tiles

    def list _is_not_alone_tiles(self) :
        #i番の牌を引いた時に孤立牌になる　　 : not_alone_tiles[i] = 0
        #i番の牌を引いた時に孤立牌にならない : not_alone_tiles[i] = 1
        def int[38] not_alone_tiles, temp
        not_alone_tiles = [0] * 38
        temp = [0] * 38
        for i in range(1, 38) :
            if self.hand[i] == 0 : continue
            if i < 30 :
                if i % 10 == 1 :
                    temp[i] = 1
                    temp[i+1] = 1
                    temp[i+2] = 1
                elif i % 10 == 2 :
                    temp[i] = 1
                    temp[i+1] = 1
                    temp[i+2] = 1
                    temp[i-1] = 1
                elif i % 10 >= 3 and i % 10 <= 7 :
                    temp[i] = 1
                    temp[i+1] = 1
                    temp[i+2] = 1
                    temp[i-1] = 1
                    temp[i-2] = 1
                elif i % 10 == 8 :
                    temp[i] = 1
                    temp[i+1] = 1
                    temp[i-2] = 1
                    temp[i-1] = 1
                elif i % 10 == 9 :
                    temp[i] = 1
                    temp[i-1] = 1
                    temp[i-2] = 1
            elif i > 30 : temp[i] = 1
        for i in range(1, 38) :
            if temp[i] == 0 : continue
            not_alone_tiles[i] = 1
        return not_alone_tiles

    def void change_score(self, int point) : self.score += point

    def void declare_riichi(self, bool first_round) :
        if first_round : self.d_riichi = True
        else : self.riichi = True
        self.ippatsu = True
        ##print("player %d riichi" % self.player_num)
        ##print(self.score)
        self.score -= 1000
        ##print(self.score)

    def void get_tile(self, int tile, bool first_hand = False) :
        self.tsumo = tile
        if tile in [0, 10, 20] :
            if first_hand is False : self.tsumo_tiles.append(51 + (tile // 10))
            self.red[(tile//10)] = True
            tile += 5
        elif first_hand is False : self.tsumo_tiles.append(tile + 10)
        self.hand[tile] += 1

    def int discard_tile(self) :
        def int discarded_tile = self.action[0]
        self.discarded_state += [self.action[4]]
        self.discarded_tiles += [discarded_tile]
        if self.action[3] is False :
            if discarded_tile in [0, 10, 20] : self.behavior.append(51 + (discarded_tile // 10))
            else : self.behavior.append(discarded_tile + 10)
        else :
            if discarded_tile in [0, 10, 20] : self.behavior.append("r" + str(51 + (discarded_tile // 10)))
            else : self.behavior.append("r" + str(discarded_tile + 10))
        if discarded_tile in [0, 10, 20] :
            self.red[discarded_tile // 10] = False
            discarded_tile += 5
        self.hand[discarded_tile] -= 1
        self.furiten_tiles[discarded_tile] += 1
        self.discarded_tiles_hist[discarded_tile] += 1
        return self.action[0]

    def void check_is_ready(self) :
        if (self.calc_syanten_num_of_normal() == 0) and self.has_used_up_winning_tile() or \
           self.calc_syanten_num_of_chiitoi() == 0 or \
           self.calc_syanten_num_of_kokushi() == 0 : self.ready = True
        else : self.ready = False

    def bool has_used_up_winning_tile(self) :
        #天鳳の処理はこうなってるはず
        #天鳳では3pを加カンしている状態で嵌3p待ちでもテンパイ扱いだったし，2015年のデータによるテストでは点数に誤差がでていない
        #(きっとおかしいんだけどね)
        def int[38] effective_tiles, hand
        def int num_of_winning_tile, i
        effective_tiles = self.effective_tiles_of_normal()
        hand = self.hand
        num_of_winning_tile = 0
        for i in range(38) :
            if effective_tiles[i] == 0 : continue
            #print(i)
            num_of_winning_tile += 4
            num_of_winning_tile -= hand[i]
        if num_of_winning_tile == 0 : return False
        return True


    def void check_all_discarded_tiles_are_edge_tiles(self) :
        if self.action[0] in [1,9,11,19,21,29,31,32,33,34,35,36,37] : dummy = True
        else : self.all_discarded_tiles_are_edge_tiles = False

    def void set_furiten_tile(self, tile) : self.furiten_tiles[tile] += 1

    def void set_round_furiten_tile(self, tile) :
        self.round_furiten_tiles += [tile]
        self.furiten_tiles[tile] += 1

    def void reset_round_furiten(self) :
        def int i
        for i in self.round_furiten_tiles : self.furiten_tiles[i] -= 1
        self.round_furiten_tiles = []

    def void set_win(self, bool state) : self.win = True
    def void set_ippatsu(self, bool state) : self.ippatsu = state
    def void set_all_discarded_tiles_are_edge_tiles(self, bool state) : self.all_discarded_tiles_are_edge_tiles = state

    def put_back_displayed_hand(self) :
        """
        displayed_hand =
        [[0+4*n]　フーロの種類（0＝フーロなし、1＝ポン、2＝チー、3＝アンカン、4＝ミンカン　5＝カカン）
        [1+4*n]　そのフーロメンツのうち最も小さい牌番号
        [2+4*n]　そのフーロメンツのうち鳴いた牌の牌番号
        [3+4*n]　その人から相対的に見た、鳴いた他家の番号。1＝下家、2＝対面、3＝上家
        [4*4*n]  副露した直後に切った牌
        ]
        """
        def int[38] hand
        def int i, n
        hand = self.hand
        for i in range(0,20,5) :
            if self.displayed_hand[i] == 0 : break
            elif self.displayed_hand[i] == Block.PON : hand[self.displayed_hand[i+1]] += 3
            elif self.displayed_hand[i] == Block.CHI :
                n = self.displayed_hand[i+1]
                hand[n] += 1
                hand[n+1] += 1
                hand[n+2] += 1
            else : hand[self.displayed_hand[i+1]] += 4
        return hand

    def bool judge_win(self, Game game, int ron_tile = -1) :
        if not(self.can_win(game, ron_tile)) : return False
        #和了するかどうかの判定 とりあえず和了れる時は和了るようにしとく Trueを返すと和了ったと判断
        self.win = True
        return self.win

    def int judge_pon_or_kan(self, int tile) :
        def int pon_kan_action
        def bool red
        if tile in [0, 10, 20] :
            tile += 5
            red = True
        else : red = False
        if self.hand[tile] < 2 : return 0
        pon_kan_action = 0 #0:スルー, 1:ポン, 2: カン
        return pon_kan_action

    def int judge_chii(self, int tile) :
        def int chii_action, tile1, tile2
        def bool red
        chii_action = 0 #0:スルー, 1:下, 2:嵌, 3,上
        if tile in [0, 10, 20] :
            tile += 5
            red = True
        else : red = False
        ###チーできるかどうかの判定
        ###チーするかどうかの判定
        if chii_action == 0 :
            tile1 = -1
            tile2 = -1
        if chii_action == 1 :
            tile1 = tile - 2
            tile2 = tile - 1
        elif chii_action == 2 :
            tile1 = tile - 1
            tile2 = tile + 1
        else :
            tile1 = tile + 1
            tile2 = tile + 2
        return chii_action, tile1, tile2

    def bool can_win(self, Game game, int ron_tile) :
        #和了れるかどうかの判定
        def bool ron, is_chiitoi, is_kokushi, is_normal
        if self.calc_syanten_num_of_chiitoi(ron_tile) == -1 : is_chiitoi = True
        else : is_chiitoi = False
        if self.calc_syanten_num_of_kokushi(ron_tile) == -1 : is_kokushi = True
        else : is_kokushi = False
        if self.calc_syanten_num_of_normal(ron_tile) == -1 : is_normal = True
        else : is_normal = False
        if not(is_chiitoi or is_kokushi or is_normal) : return False
        if ron_tile > -1 :
            ron = True
            if ron_tile in [0,10,20] : ron_tile += 5
            if self.is_furiten(is_chiitoi, is_kokushi, is_normal, ron_tile) : return False
        else : ron = False
        if self.judge_if_there_is_yaku(game, ron, ron_tile) : return True
        return False

    def bool is_furiten(self, bool is_chiitoi, bool is_kokushi, bool is_normal, int ron_tile) :
        def int[38] hand, effective_tiles
        hand = self.hand
        if is_chiitoi :
            if self.furiten_tiles[ron_tile] > 0 : return True
        if is_kokushi :
            effective_tiles = self.effective_tiles_of_kokushi()
            for i in [1,9,11,19,21,29,31,32,33,34,35,36,37] :
                if self.furiten_tiles[i] > 0 and effective_tiles[i] > 0 : return True
        if is_normal :
            effective_tiles = self.effective_tiles_of_normal()
            for i in range(1, 38) :
                if i % 10 == 0 : continue
                if self.furiten_tiles[i] > 0 and effective_tiles[i] > 0 : return True
        return False

    def bool judge_if_there_is_yaku(self, Game game, bool ron, int ron_tile) :
        def int[38] hand
        def int round_wind, seat_wind
        if self.riichi : return True
        if self.d_riichi : return True
        hand = self.put_back_displayed_hand()
        if tanyao(hand) : return True
        if haku(hand) : return True
        if hatsu(hand) : return True
        if chun(hand) : return True
        round_wind = 31 + game.game_round
        if bakaze(hand, round_wind) : return True
        seat_wind = 31 + (((self.player_num + 4) - game.game_num)%4)
        if jikaze(hand, seat_wind) : return True
        if not(ron) and not(self.displayed_tf) : return True
        if honitsu(hand) : return True
        if chinitsu(hand) : return True
        if haitei(game.p_wall, game.p_rinsyan, ron) : return True
        if houtei(game.p_wall, game.p_rinsyan, ron) : return True
        if chankan(game.kakan_flag, ron) : return True
        if rinsyan(game.minkan_flag, game.ankan_flag, ron) : return True
        if tenhou(game.first_round, ron, game.game_num, self.player_num) : return True
        if chiihou(game.first_round, ron, game.game_num, self.player_num) : return True
        if self._judge_if_there_is_hand_composition_yaku(round_wind, seat_wind, ron, ron_tile) : return True

    def bool _judge_if_there_is_hand_composition_yaku(self, int round_wind, int seat_wind, bool ron, int ron_tile) :
        def int[38] hand
        def bool there_is_yaku
        hand = self.hand
        if ron : hand[ron_tile] += 1
        self.composition_of_hand = [0] * 10
        #副露メンツ確定
        for i in range(0,4) :
            if self.displayed_hand[i*5] != 0 :
                self.composition_of_hand[(i*2)] = self.displayed_hand[i*5]
                self.composition_of_hand[(i*2)+1] = self.displayed_hand[(i*5)+1]
                self.p_composition_of_hand += 2
            else : break
        #頭抜き出し
        for i in range(1,38) :
            if hand[i] == 0 : continue
            if hand[i] >= 2 :
                hand[i] = hand[i] - 2
                self.composition_of_hand[self.p_composition_of_hand] = Block.TOITSU
                self.composition_of_hand[self.p_composition_of_hand+1] = i
                self.p_composition_of_hand += 2
                there_is_yaku = self._pick_out_mentsu_for_composition_hand(hand, round_wind, seat_wind, ron, ron_tile);
                if there_is_yaku : return True
                self.p_composition_of_hand -= 2
                self.composition_of_hand[self.p_composition_of_hand] = 0
                self.composition_of_hand[self.p_composition_of_hand+1] = 0
                hand[i] = hand[i] + 2
        return False

    def bool _pick_out_mentsu_for_composition_hand(self, int[:] hand, int round_wind, int seat_wind, bool ron, int ron_tile) :
        def int i
        for i in range(1,38) :
            if self.composition_of_hand[9] != 0 :
                if pinfu(self.composition_of_hand, ron_tile, round_wind, seat_wind) : return True
                if iipeikou(self.composition_of_hand) : return True
                if chanta(self.composition_of_hand) : return True
                if sansyokudoujun(self.composition_of_hand) : return True
                if ikkitsuukan(self.composition_of_hand) : return True
                if toitoi(self.composition_of_hand) : return True
                if sansyokudoukou(self.composition_of_hand) : return True
                if sankantsu(self.composition_of_hand) : return True
                if sanankou(self.composition_of_hand) : return True
                if junchanta(self.composition_of_hand) : return True
                return False
            if hand[i] == 0 : continue
            #暗刻抜き出し
            if hand[i] >= 3 :
                hand[i] -= 3
                if i == ron_tile and ron and hand[i] == 0 : self.composition_of_hand[self.p_composition_of_hand] = Block.PON
                else : self.composition_of_hand[self.p_composition_of_hand] = Block.ANKO
                self.composition_of_hand[self.p_composition_of_hand+1] = i
                self.p_composition_of_hand += 2
                self._pick_out_mentsu_for_composition_hand(hand, round_wind, seat_wind, ron, ron_tile)
                self.p_composition_of_hand -= 2
                self.composition_of_hand[self.p_composition_of_hand] = 0
                self.composition_of_hand[self.p_composition_of_hand+1] = 0
                hand[i] += 3
            #順子抜き出し
            if i < 30 and hand[i] != 0 and hand[i+1] != 0 and hand[i+2] != 0 :
                hand[i] = hand[i] - 1
                hand[i+1] = hand[i+1] - 1
                hand[i+2] = hand[i+2] - 1
                self.composition_of_hand[self.p_composition_of_hand] = Block.SYUNTSU
                self.composition_of_hand[self.p_composition_of_hand+1] = i
                self.p_composition_of_hand += 2
                self._pick_out_mentsu_for_composition_hand(hand, round_wind, seat_wind, ron, ron_tile)
                self.p_composition_of_hand -= 2
                self.composition_of_hand[self.p_composition_of_hand+1] = 0
                self.composition_of_hand[self.p_composition_of_hand] = 0
                hand[i] += 1
                hand[i+1] += 1
                hand[i+2] += 1

    def bool judge_9_kinds(self) :
        def int i, num_edge_tile
        num_edge_tile = 0
        for i in [1,9,11,19,21,29,31,32,33,34,35,36,37] :
            if self.hand[i] > 0 : num_edge_tile += 1
        #今はとりあえず流局できたらするようにする
        if num_edge_tile > 8 :
            ###print("drawn game : 9 kinds")
            return True
        else : return False

    def list set_action(self, action) : self.action = action

    def void proc_ankan(self) :
        def int tile
        def str s
        tile = self.action[0]
        if tile in [0,10,20] : tile += 5
        self.displayed_hand[self.displayed_num * 5] = 3
        self.displayed_hand[self.displayed_num * 5 + 1] = tile
        self.displayed_hand[self.displayed_num * 5 + 2] = tile
        self.displayed_hand[self.displayed_num * 5 + 3] = 0
        self.hand[tile] -= 4
        self.displayed_num += 1
        self.num_of_kan += 1
        s = str(tile + 10)
        self.behavior.append(s+s+s+"a"+s)

    def void proc_kakan(self) :
        def int tile, i
        def str s
        tile = self.action[0]
        self.num_of_kan += 1
        if tile in [0,10,20] : tile += 5
        for i in range(4) :
            if self.displayed_hand[i*5] == 1 and self.displayed_hand[(i*5)+1] == tile :
                self.displayed_hand[i*5] = 4
                self.hand[tile] -= 1
                s = str(tile + 10)
                if self.displayed_hand[i*5+3] == 1 : self.behavior.append(s+s+"k"+s+s)
                elif self.displayed_hand[i*5+3] == 1 : self.behavior.append(s+"k"+s+s+s)
                else : self.behavior.append("k"+s+s+s+s)
                break

    def void proc_minkan(self, int tile, int p) :
        def int place
        place = (4 + p - self.player_num) % 4
        if tile in [0,10,20] :
            if place == 1 : self.behavior.append(str(tile+15) + str(tile+15) + str(tile+15) + "m" + str(51+(tile // 10)))
            elif place == 2 : self.behavior.append(str(tile+15) + "m" + str(tile+15) + str(51+(tile // 10)) + str(tile+15))
            else : self.behavior.append("m" + str(51+(tile // 10)) + str(tile+15) + str(tile+15) + str(tile+15))
            self.red[tile // 10] = True
            tile += 5
        elif tile in [5,15,25] and self.red[tile // 10] :
            if place == 1 : self.behavior.append(str(tile + 10) + str(tile + 10) + str(51 + (tile // 10)) + "m" + str(tile + 10))
            elif place == 2 : self.behavior.append(str(tile + 10) + "m" + str(tile + 10) + str(tile + 10) + str(51 + (tile // 10)))
            else : self.behavior.append("m" + str(tile + 10) + str(51 + (tile // 10)) + str(tile + 10) + str(tile + 10))
        elif place == 1 : self.behavior.append(str(tile + 10) + str(tile + 10) + str(tile + 10) + "m" + str(tile + 10))
        elif place == 2 : self.behavior.append(str(tile + 10) + "m" + str(tile + 10) + str(tile + 10) + str(tile + 10))
        elif place == 3 : self.behavior.append("m" + str(tile + 10) + str(tile + 10) + str(tile + 10) + str(tile + 10))
        else : ###print("error proc_minkan")
            dummy = True
        self.hand[tile] -= 3
        self.displayed_hand[(self.displayed_num * 5) + 0] = 4
        self.displayed_hand[(self.displayed_num * 5) + 1] = tile
        self.displayed_hand[(self.displayed_num * 5) + 2] = tile
        self.displayed_hand[(self.displayed_num * 5) + 3] = place
        self.displayed_num += 1
        self.displayed_tf = True
        self.num_of_kan += 1

    def void proc_pon(self, int tile, int p, Game game) :
        def int place, min_tile
        place = (4 + p - self.player_num) % 4
        if tile in [0,10,20] :
            red = True
            if place == 1 : self.behavior.append(str(tile+15) + str(tile+15) + "p" + str(51+(tile // 10)))
            elif place == 2 : self.behavior.append(str(tile+15) + "p" + str(51+(tile // 10)) + str(tile+15))
            else : self.behavior.append("p" + str(51+(tile // 10)) + str(tile+15) + str(tile+15))
            self.red[tile // 10] = True
            tile += 5
        elif tile in [5,15,25] and self.red[tile // 10] :
            if place == 1 : self.behavior.append(str(tile + 10) + str(51 + (tile // 10)) + "p" + str(tile + 10))
            elif place == 2 : self.behavior.append(str(tile + 10) + "p" + str(tile + 10) + str(51 + (tile // 10)))
            else : self.behavior.append("p" + str(tile + 10) + str(51 + (tile // 10)) + str(tile + 10))
        elif place == 1 : self.behavior.append(str(tile + 10) + str(tile + 10) + "p" + str(tile + 10))
        elif place == 2 : self.behavior.append(str(tile + 10) + "p" + str(tile + 10) + str(tile + 10))
        elif place == 3 : self.behavior.append("p" + str(tile + 10) + str(tile + 10) + str(tile + 10))
        else : ###print("error proc_pon")
            dummy = True
        self.hand[tile] -= 2
        self.displayed_hand[(self.displayed_num * 5) + 0] = 1
        self.displayed_hand[(self.displayed_num * 5) + 1] = tile
        self.displayed_hand[(self.displayed_num * 5) + 2] = tile
        self.displayed_hand[(self.displayed_num * 5) + 3] = place
        self.displayed_num += 1
        self.displayed_tf = True
        if tile in [35, 36, 37] :
            self.num_of_dragon += 1
            if self.num_of_dragon == 3 : game.set_pao_of_3_dragons(self.player_num, p)
        elif tile in [31, 32, 33, 34] :
            self.num_of_winds += 1
            if self.num_of_winds == 4 : game.set_pao_of_4_winds(self.player_num, p)

    def proc_chii(self, int tile, int tile1, int tile2) :
        if tile in [0,10,20] :
            self.behavior.append("c" + str(51 + (tile // 10)) + str(tile1 + 10)+str(tile2 + 10))
            self.red[tile // 10] = True
            tile += 5
            tile1 += 5
            tile2 += 5
        elif tile1 in [5,15,25] and self.red[tile1 // 10] :
            self.behavior.append("c" + str(tile + 10) + str(51 + (tile1 // 10)) + str(tile2 + 10))
        elif tile2 in [5,15,25] and self.red[tile1 // 10] :
            self.behavior.append("c" + str(tile + 10) + str(tile1 + 10) + str(51 + (tile2 // 10)))
        else : self.behavior.append("c" + str(tile + 10) + str(tile1 + 10) + str(tile2 + 10))
        self.hand[tile1] -= 1
        self.hand[tile2] -= 1
        self.displayed_hand[(self.displayed_num * 5) + 0] = 2
        if tile1 > tile : min_tile = tile
        else : min_tile = tile1
        self.displayed_hand[(self.displayed_num * 5) + 1] = min_tile
        self.displayed_hand[(self.displayed_num * 5) + 2] = tile
        self.displayed_hand[(self.displayed_num * 5) + 3] = 3
        self.displayed_num += 1
        self.displayed_tf = True

    #鳴いた後の手出し牌を登録
    def void add_tile_player_discard_after_displaying(self, int tile) : self.displayed_hand[((self.displayed_num - 1) * 5) + 4] = tile

    def void print_hand(self) :
        def str s_hand
        #受け取った手牌を表示
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
        #print(s_hand)

    def void add_to_first_hand(self, int tile) :
        if tile in [0, 10, 20] : tile = 51 + (tile // 10)
        else : tile += 10
        self.first_hand.append(tile)

    def void set_hand(self) :
        def int[38] hand
        hand = [0] * 38
        for i in range(2) :
            hand[21] += 1
            hand[29] += 1
        for i in range(21, 30) : hand[i] += 1
        self.hand = hand
