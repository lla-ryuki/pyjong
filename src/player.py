#std
import random
from typing import List

# 3rd

# ours
from game import Game
from block import Block
from tile_type import TileType


"""
TODO
ツモ切りのDとd逆にしたい
tile, exchanged, ready, ankan, kakan, kyushu = players[self.i_player].decide_action(self, players)
loggerの処理切り分けてく
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
        self.is_nagashi_mangan = True                     # 流し満貫継続中か

        self.wins = False                                 # 和了ったか

        self.opened_sets_num = 0                          # 晒している面子の数(暗槓含む)
        self.kans_num = 0                                 # 槓した回数

        self.players_wind = 31 + self.player_num          # 自風
        self.last_added_tile = -1                         # 直近でツモった牌 赤牌は番号そのまま(10:赤5筒)

        # アクションフェーズ用
        self.last_discarded_tile = -1                     # 最後に切った牌 赤牌は番号そのまま(10:赤5筒)
        self.exchanged = False
        self.ready = False
        self.anakn = False
        self.kakan = False
        self.kyushu = False

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
        self.last_added_tile = -1                         # 直近でツモった牌 赤牌は番号そのまま(10:赤5筒)
        self.last_discarded_tile = -1                     # 最後に切った牌 赤牌は番号そのまま(10:赤5筒)

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



    # 国士無双の向聴数を返す
    def calc_syanten_num_of_kokushi(self, tile:int = -1 ) :
        hand = deepcopy(self.hand) # handに牌を足す可能性がある時は元のhandが壊れないようにコピーを作る

        if tile > -1 :
            if tile in TileType.REDS :
                tile += 5
            hand[tile] += 1

        pairs_num = 0
        syanten_num = 13

        for i in (TileType.TERMINALS | TileType.HONORS) :
            if hand[i] != 0 : syanten_num -= 1
            if hand[i] > 1 and pairs_num == 0 : pairs_num = 1

        syanten_num -= pairs_num
        self.syanten_num_of_kokushi = syanten_num

        return syanten_num


    # 国士無双の有効牌のリストを返す
    def effective_tiles_of_kokushi(self) -> list :
        hand = deepcopy(self.hand)
        effective_tiles = [0] * 38

        syanten_num = self.calc_syanten_num_of_kokushi()
        for i in (TileType.TERMINALS | TileType.HONORS) :
            if self.calc_syanten_num_of_kokushi(i) < syanten_num : effective_tiles[i] = 1

        return effective_tiles


    # 七対子の向聴数を返す
    def calc_syanten_num_of_chiitoi(self, tile: int = -1) -> int :
        hand = deepcopy(self.hand)

        if tile > -1 :
            if tile in TileType.REDS : tile += 5
            hand[tile] += 1

        syanten_num = 6
        kind = 0 # 6対子あっても孤立牌がないと聴牌にならないのでそれのチェック用
        for i in range(1,38) :
            if hand[i] >= 1 :
                kind += 1
            if hand[i] >= 2 :
                syanten_num -= 1
        if kind < 7 :
            syanten_num += 7 - kind

        self.syanten_num_of_chiitoi = syanten_num

        return syanten_num


    # 七対子の有効牌のリストを返す
    def effective_tiles_of_chiitoi(self) -> list :
        effective_tiles = [0] * 38
        syanten_num = self.calc_syanten_num_of_chiitoi()
        for i in range(38) :
            if i % 10 == 0 : continue
            if self.calc_syanten_num_of_chiitoi(i) < syanten_num : effective_tiles[i] = 1

        return effective_tiles


    # 通常手の向聴数を返す
    def calc_syanten_num_of_normal(self, tile: int = -1) :
        hand = deepcopy(self.hand)
        self.syanten_num_of_normal = 8
        self.sets_num = self.opened_sets_num
        self.pairs_num = 0
        self.tahtsu_num = 0

        if tile > -1 :
            if tile in TileType.REDS : tile += 5
            hand[tile] += 1

        for i in range(1,38) :
            if hand[i] >= 2 :
                self.n_pair += 1
                hand[i] -= 2
                self._pick_out_mentsu(1, hand)
                hand[i] += 2
                self.n_pair -= 1
        self._pick_out_mentsu(1, hand)

        return self.syanten_num_of_normal


    # 面子を抜き出す
    def _pick_out_mentsu(self, i:int , hand: List[int]) -> None :
        while i < 38 and hand[i] == 0 : i += 1
        if i > 37 :
            self._pick_out_tahtsu(1, hand)
            return
        if hand[i] > 2 :
            self.mentsu_num += 1
            hand[i] -= 3
            self._pick_out_mentsu(i, hand)
            hand[i] += 3
            self.mentsu_num -= 1
        if  i < 28 and hand[i+1] > 0 and hand[i+2] > 0 :
            self.mentsu_num += 1
            hand[i] -= 1
            hand[i+1] -= 1
            hand[i+2] -= 1
            self._pick_out_mentsu(i, hand)
            hand[i] += 1
            hand[i+1] += 1
            hand[i+2] += 1
            self.mentsu_num -= 1
        self._pick_out_mentsu(i+1, hand)


    # 塔子を抜き出す
    def _pick_out_tahtsu(self, i: int, hand: List[int]) -> None :
        while i < 38 and hand[i] == 0 : i += 1
        if i > 37 :
            self.syanten_num_of_temp = 8 - self.mentsu_num * 2 - self.n_tahtsu - self.n_pair
            if self.syanten_num_of_temp < self.syanten_num_of_normal :
                self.syanten_num_of_normal = self.syanten_num_of_temp
            return
        if self.mentsu_num + self.n_tahtsu < 4 :
            if hand[i] == 2 :
                self.n_tahtsu += 1
                hand[i] -= 2
                self._pick_out_tahtsu(i, hand)
                hand[i] += 2
                self.n_tahtsu -= 1
            if i < 29 and hand[i+1] != 0 :
                self.n_tahtsu += 1
                hand[i] -= 1
                hand[i+1] -= 1
                self._pick_out_tahtsu(i, hand)
                hand[i] += 1
                hand[i+1] += 1
                self.n_tahtsu -= 1
            if i < 29 and i % 10 < 9 and hand[i+2] != 0 :
                self.n_tahtsu += 1
                hand[i] -= 1
                hand[i+2] -= 1
                self._pick_out_tahtsu(i, hand)
                hand[i] += 1
                hand[i+2] += 1
                self.n_tahtsu -= 1
        self._pick_out_tahtsu(i+1, hand)


    # 通常手の有効牌のリストを返す
    def effective_tiles_of_normal(self) -> list :
        effective_tiles = [0] * 38
        not_alone_tiles = self._is_not_alone_tiles()
        syanten_num = self.calc_syanten_num_of_normal()

        for i in range(1, 38) :
            if not_alone_tiles[i] == 0 : continue
            if self.calc_syanten_num_of_normal(i) < syanten_num : effective_tiles[i] = 1
        return effective_tiles


    # ある牌を引いた時孤立牌になるかどうかの情報が入ったリストを返す
    ## i番の牌を引いた時に孤立牌になる　　 : not_alone_tiles[i] = 0
    ## i番の牌を引いた時に孤立牌にならない : not_alone_tiles[i] = 1
    def _is_not_alone_tiles(self) -> list :
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
    def score_points(self, points: int) -> None :
        self.score += points


    # 立直宣言
    def declare_ready(self, is_first_turn: bool) -> None :
        if is_first_turn : self.has_declared_double_ready = True
        else : self.has_declared_ready = True
        self.has_right_to_one_shot = True
        self.score -= 1000


    # 牌を手牌に加える．配牌取得，ツモ，ロンで使う．
    ### get_tile()にするとgetterと紛らわしいのでこの名前になった.もうちょっといい名前ないか?
    ### ツモる時以外にも使うのでdraw_tile()は相応しくないと判断
    def add_tile_to_hand(self, tile: int, starting_hand: bool = False) -> None :
        self.last_added_tile = tile
        if tile in TileType.REDS :
            if starting_hand is False : self.tsumo_tiles.append(51 + (tile // 10))
            self.reds[tile//10] = True
            tile += 5
        elif starting_hand is False : self.tsumo_tiles.append(tile + 10)
        self.hand[tile] += 1


    # 牌を捨てる
    ## ここで捨てる牌を決めるわけではない．捨てる牌はdecide_action()で決める．
    def discard_tile(self) -> int :
        discarded_tile = self.last_discarded_tile

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
    def check_is_ready(self) -> bool :
        if (self.calc_syanten_num_of_normal() == 0) and self.has_used_up_winning_tile() or \
           self.calc_syanten_num_of_chiitoi() == 0 or \
           self.calc_syanten_num_of_kokushi() == 0 : self.is_ready = True
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
    def add_furiten_tile(self, tile) -> None : self.furiten_tiles[tile] += 1


    # 同巡フリテン牌を追加
    def add_same_turn_furiten_tile(self, tile: int) -> None :
        self.same_turn_furiten_tiles += [tile]
        self.furiten_tiles[tile] += 1


    # 同巡フリテンを解消
    def reset_same_turn_furiten(self) -> None :
        for i in self.same_turn_furiten_tiles : self.furiten_tiles[i] -= 1
        self.same_turn_furiten_tiles = []


    # 鳴いて晒した牌を全部戻した手をreturnする
    def put_back_opened_hand(self) -> List[int] :
        """
        opened_hand =
        [[0+4*n]　フーロの種類（0＝フーロなし、1＝ポン、2＝チー、3＝アンカン、4＝ミンカン　5＝カカン）
        [1+4*n]　そのフーロメンツのうち最も小さい牌番号
        [2+4*n]　そのフーロメンツのうち鳴いた牌の牌番号
        [3+4*n]　その人から相対的に見た、鳴いた他家の番号。1＝下家、2＝対面、3＝上家
        [4*4*n]  副露した直後に切った牌
        ]
        """
        hand = self.hand[:]
        for i in range(0,20,5) :
            if self.opened_hand[i] == 0 : break
            elif self.opened_hand[i] == Block.OPENED_TRIPLET : hand[self.opened_hand[i+1]] += 3
            elif self.opened_hand[i] == Block.OPENED_RUN :
                n = self.opened_hand[i+1]
                hand[n] += 1
                hand[n+1] += 1
                hand[n+2] += 1
            else : hand[self.opened_hand[i+1]] += 4
        return hand


    # 和了するかどうかの判定
    def decide_win(self, game: Game, ron_tile: int = -1) -> bool :
        # そもそも和了れるかどうかの判定
        # TODO ここじゃなくてgame.pyの中でやった方がいい気がするよね...
        if not(self.can_win(game, ron_tile)) : return False

        # TODO 和了るかどうかの判断　今は和了れたら和了るようにしている
        self.wins = True

        return self.wins


    # ポン or 大明槓するかどうかの判断
    def decide_pon_or_kan(self, tile: int) -> int :
        red = False
        if tile in TileType.REDS :
            tile += 5
            red = True

        # そもそもポン or 大明槓できるかの判定
        if self.hand[tile] < 2 : return 0

        # TODO ポンするかどうかの判断　今は鳴かないようにしている
        pon = False
        kan = False

        return pon, kan


    # チーするかどうかの判断
    def decide_chii(self, tile: int) -> (bool, int, int) :
        red = False
        if tile in TileType.REDS :
            tile += 5
            red = True

        # チーできるかどうかの判定
        if self.can_chii(tile) is False : return chii, -1, -1

        ### TODO チーするかどうかの判断
        ### chii_action:0 => スルー
        ### chii_action:1 => 下チー
        ### chii_action:2 => 嵌張チー
        ### chii_action:3 => 上チー
        ### がNNから帰ってくるようにしたい

        # 返り値の処理
        chii = False
        chii_action = 0 ### 今はチーできないようにしている
        if chii_action == 0 : tile1, tile2 = -1, -1
        elif chii_action == 1 : chii, tile1, tile2 = True, (tile - 2), (tile - 1)
        elif chii_action == 2 : tile1, tile2 = True, (tile-1), (tile + 1)
        elif chii_action == 3 : tile1, tile2 = True, (tile+1), (tile + 2)
        else : tile1, tile2 = -1, -1 # 想定しない処理　一応

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

    def list decide_action(self, action) : self.action = action

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

    def void add_to_starting_hand(self, int tile) :
        if tile in [0, 10, 20] : tile = 51 + (tile // 10)
        else : tile += 10
        self.starting_hand.append(tile)

    def void set_hand(self) :
        def int[38] hand
        hand = [0] * 38
        for i in range(2) :
            hand[21] += 1
            hand[29] += 1
        for i in range(21, 30) : hand[i] += 1
        self.hand = hand


    # 暗槓できるかどうか判定，できる場合は暗槓できる牌の牌番号のリストを返す
    def _can_ankan(self, game: Game) -> List[int] :
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



    # 槓しないか or どの牌で槓するか決める
    def _deside_which_tile_to_kan(self, game: Game, playes: List[Player]) -> int :
        ### 今は強制的に槓しないようにする
        ### NNの計算とかが入る
        return -1


    # 槓するかどうか決める
    def _decide_to_kan(self, game, players) :
        tile, ankan, kakan = -1, False, False

        # 槓できるか判定
        can_ankan_tiles = self._can_ankan(game)
        can_kakan_tiles = self._can_kakan(game)

        # プレイヤが槓の内容（どの牌で槓するか，しないか）を決める
        tile = self._deside_which_tile_to_kan(game, players)
        if tile in can_ankan_tiles : ankan = True
        elif tile in can_kakan_tiles : kakan = True
        else : tile = -1 # deside_which_tile_to_kan()でとんでもないものが帰ってきたときにバグらないように一応制御

        return tile, ankan, kakan

    def decide_action(self, game, players) :
        # プレイヤの行動決定，tile:赤は(0,10,20)表示
        tile, ankan, kakan, ready, exchanged = -1, False, False, False, False
        dummy = None

        # 槓するかどうか決める
        tile, ankan, kakan = self._decide_to_kan()
        if ankan or kakan : return tile, ankan, kakan, ready, exchanged

        # 切る牌を決める．赤は(0, 10, 20)．
        tile = self.deside_which_tile_to_discard()

        # 立直するかどうか決める
        ready = self.decide_to_declare_ready(tile)

        return tile, ankan, kakan, ready, exchanged
