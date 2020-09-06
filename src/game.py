#std
import random
from copy import deepcopy
from typing import List

# 3rd

# ours
from player import Player
from block import Block
from tile_type import TileType
from logger import Logger
from yaku import *
from yakuman import *


"""
Gameクラス
イメージはゲームモデルでいうEnvironmentとAgentの複合体
    Environment : あらゆる状態を保有するもの
    Agent       : 状態を操作したり，何かを判定するもの
"""
class Game :


    def __init__(self) :
        self.rounds_num = 0                             # 場 0:東場，1:南場，2:西場
        self.rotations_num = 0                          # 局 0:1局目 ... 3:4局目
        self.counters_num = 0                          # 積み棒の数
        self.deposits_num = 0                          # 供託の数
        self.prevailing_wind = 31 + self.rounds_num     # 場風にあたる牌番号
        self.is_abortive_draw = False                  # 途中流局になるとTrueになる
        self.is_first_turn = True                      # Trueの間は1巡目であることを示す
        self.is_over = False                           # Trueになると半荘終了
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

        # 牌の状態
        self.doras = [0] * 5                           # ドラ
        self.dora_indicators = [0] * 5                 # ドラ表示牌
        self.uras = [0] * 5                            # 裏
        self.ura_indicators = [0] * 5                  # 裏表示牌
        self.dora_has_opened = [False] * 5             # ドラの状態, i番目がTrue → dora_indicators[i]がめくれている状態
        self.rinshan_tiles = [0] * 4                   # 嶺上牌
        self.appearing_tiles = [0] * 38                # プレイヤ全員に見えている牌， appearing_tiles[i] が j → i番の牌がj枚見えている
        self.appearing_red_tiles = [False] * 3         # プレイヤ全員に見えている赤牌． 萬子，筒子，索子の順．
        self.wall = [0] * 136                          # 山

        # インデックス
        self.i_player = 0                              # 次のループで行動するプレイヤの番号
        self.i_wall = 0                                # 山用のインデックス
        self.i_rinshan = 0                             # 嶺上牌用のインデックス
        self.i_first_turn = 0                          # 最初の1巡目かどうかを判定するために使うインデックス

        ######
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
        self.daiminkan_flag = False                    # 大明槓処理用
        self.kakan_flag = False                        # 加槓処理用
        self.ankan_flag = False                        # 暗槓処理用
        self.has_stealed_flag = False                  # 手出し処理用


    # 局開始時の初期化
    def init_subgame(self) -> None :
        self.i_player = self.rotations_num
        ### 書く必要あるで


    # 赤有りの牌山を生成
    def _set_wall_containing_red(self) -> None :
        i, red = 0, False
        for j in range(1,38) :
            if j in Kinds.blanks : continue
            if j in Kinds.fives : red = True
            for k in range(4) :
                if red :
                    self.wall[i] = j - 5
                    red = False
                else :
                    self.wall[i] = j
                i += 1
        random.shuffle(self.wall)


    #ドラと裏ドラをセット
    def _set_doras(self) -> None :
        # ドラ表示牌, 裏ドラ表示牌をセット
        self.dora_indicators = [self.wall[i] for i in range(130, 121, -2)]
        self.ura_indicators = [self.wall[i] for i in range(131, 122, -2)]

        for i in range(5) :
            # ドラをセット
            if dora_indicators[i] in Kinds.reds : indicator = dora_indicators[i] + 5
            else : indicator = dora_indicators[i]
            if indicator in Kinds.nines : doras[i] = indicator - 8
            elif indicator == 34 : doras[i] = 31
            elif indicator == 37 : doras[i] = 35
            else : doras[i] = indicator + 1

            # 裏ドラをセット
            if ura_indicators[i] in Kinds.reds : indicator = ura_indicators[i] + 5
            else : indicator = ura_indicators[i]
            if ura_indicator in Kinds.nines : uras[i] = ura_indicator - 8
            elif ura_indicator == 34 : uras[i] = 31
            elif ura_indicator == 37 : uras[i] = 35
            else : uras[i] = ura_indicator + 1


    # 嶺上牌をセット
    def _set_rinshan_tiles(self) -> None :
        self.rinshan_tiles = [self.wall[134], self.wall[135], self.wall[132], self.wall[133]]


    # 新しいドラを開く
    def open_new_dora(self) -> None :
        for i in range(5) :
            if self.dora_has_opened[i] is False :
                self.dora_has_opened[i] = True
                self.appearing_tiles[self.dora_indicators[i]] += 1
                break


    # 次のツモ牌を返す
    def supply_next_tile(self) -> int :
        tile = self.wall[self.i_wall]
        self.i_wall += 1
        return tile


    # 次の嶺上牌を返す
    def supply_next_rinshan_tile(self) -> int :
        tile = self.rinshan_tiles[self.i_rinshan]
        self.i_rinshan += 1
        return tile


    # 四槓散了判定
    def _check_four_kans(self, players: List[Player]) -> bool :
        kans_num = 0
        for i in range(4) :
            if players[i].kans_num == 4 : return False # 一人で4回槓しているのは流局にならない
            kans_num += players[i].kans_num
        if kans_num == 4 :
            self.is_abortive_draw = True
            return True
        return False


    # 暗槓が行われた時の処理
    def proc_ankan(self, tile: int) -> None :
        if tile in Kinds.reds : tile += 5
        self.appearing_tiles[tile] += 4
        self.is_first_turn = False
        self.open_new_dora()
        self.ankan_flag = True


    # 加槓が行われた時の処理
    def proc_kakan(self, tile: int) -> None :
        if tile in Kinds.reds : tile += 5
        self.appearing_tiles[tile] += 1
        self.kakan_flag = True


    # 大明槓が行われた時の処理
    def proc_daiminkan(self, tile: int, action_players_num: int) -> None :
        if tile in Kinds.reds : tile += 5
        self.appearing_tiles[tile] += 3
        self.is_first_turn = False
        self.i_player = action_players_num
        self.daiminkan_flag = True
        self.i_player = (4 + action_players_num - 1) % 4


    # ポンが行われた時の処理
    def proc_pon(self, tile: int, action_players_num : int) -> None :
        if tile in Kinds.reds : tile += 5
        self.appearing_tiles[tile] += 2
        self.is_first_turn = False
        self.has_stealed_flag = True
        self.i_player = (4 + action_players_num - 1) % 4


    # チーが行われた時の処理
    def proc_chii(self, tile: int, tile1: int, tile2: int) -> None :
        if tile in Kinds.reds :
            tile += 5
            tile1 += 5
            tile2 += 5
        self.appearing_tiles[tile1] += 1
        self.appearing_tiles[tile2] += 1
        self.has_stealed_flag = True
        self.is_first_turn = False


    # 点数計算前の準備
    def _preproc_calc_score(self, i_winner: int) -> None :
        # 親かどうかを確認
        if self.rotations_num == i_winner : self.dealer_wins = True
        else : self.dealer_wins = False
        # パオか確認
        if i_winner == self.pao_info[0] :
            self.liability_player = self.pao_info[1]
            self.wins_by_pao= True
        elif i_winner == self.pao_info[2] :
            self.liability_player = self.pao_info[3]
            self.wins_by_pao= True
        else :
            self.wins_by_pao= False
            self.liability_player = -1
        # 天和・地和かどうか確認
        if self.is_first_turn :
            if not(self.wins_by_ron) :
                if self.dealer_wins : self.wins_by_tenhou = True
                else : self.wins_by_chiihou = True



    # ロン和了の処理
    def _proc_ron(self, players: List[Player], i_winner: int) -> int :
        # 基本点から得点を算出
        if self.dealer_wins : score = self.basic_points * 6
        else : score = self.basic_points * 4

        # 点数移動
        if self.wins_by_pao:
            players[self.i_player].score(-1 * (score // 2))
            players[liability_player].score(-1 * ((score // 2) + (300 * self.counters_num)))
            players[self.i_player].score(score)
        else :
            if score % 100 != 0 : score += int(100 - (score % 100)) # 100の位で切り上げ
            players[self.i_player].score(-1 * (score + (300 * self.counters_num)))
            players[i_winner].score(score)


    # ツモ和了の処理
    def _proc_tsumo(self, players: List[Player], i_winner: int) -> int :
        if self.wins_by_pao:
            if not(self.dealer_wins) : score = self.basic_points * 4
            else : score = self.basic_points * 6
            players[liability_player].score(-1 * (score + (300 * self.counters_num)))
            players[self.i_player].score(score)
        else :
            if self.dealer_wins :
                score = self.basic_points * 2
                if score % 100 != 0 : score += (100 - (score % 100))
                for i in range(1,4) : players[(i_winner + i) % 4].score(-1 * (score + (100 * self.counters_num)))
                players[i_winner].score(score * 3)
            else :
                score_which_dealer_pay = self.basic_points * 2
                if score_which_dealer_pay % 100 != 0 : score_which_dealer_pay += (100 - (score_which_dealer_pay % 100))
                score_which_child_pay = self.basic_points
                if score_which_child_pay % 100 != 0 : score_which_child_pay += (100 - (score_which_child_pay % 100))
                for i in range(1,4) :
                    i_payer = (i_winner + i) % 4
                    if i_payer != self.rotations_num :
                        players[i_payer].score(-1 * (score_which_child_pay + (100 * self.counters_num)))
                        players[i_winner].score(score_which_child_pay)
                    else :
                        players[i_payer].score(-1 * (score_which_dealer_pay + (100 * self.counters_num)))
                        players[self.i_player].score(score_which_dealer_pay)


    # 和了時の処理
    def proc_win(self, players: List[Player]) -> None :
        counters_num_temp = self.counters_num
        # ツモった人，最後に牌を切った人から順に和了を見ていく．※ 複数人の和了の可能性があるので全員順番にチェックする必要がある．
        for i in range(4) :
            i_winner = (self.i_player + i) % 4
            if players[i_winner].wins :
                self._preproc_calc_score()
                self.basic_points = self._calc_basic_points(players[self.i_player])
                if self.wins_by_ron : self._proc_ron(i_winner)
                else : self._proc_tsumo(i_winner)
                players[i_winner].score(300 * self.counters_num)
                players[i_winner].score(1000 * self.deposits_num)
                self.counters_num, self.deposits_num = 0, 0
                if i == 0 : break
        # ゲーム終了判定
        self.is_over = self._check_game_is_over(players, players[self.rotations_num].wins)
        # 局の数等の変数操作
        if players[self.rotations_num].wins : self.counters_num += 1
        else :
            self.counters_num = 0
            self.rotations_num += 1
            if self.rotations_num == 4 :
                self.rounds_num += 1
                self.rotations_num = 0


    # 流局時の処理
    def proc_drawn_game(self, players: List[Player]) -> None :
        tenpai_players_num = 0
        for i in range(4) :
            if players[i].is_tenpai : tenpai_players_num += 1
        if tenpai_players_num != 0 and tenpai_players_num != 4 :
            not_tenpai_penalty = 3000 // tenpai_players_num
            tenpai_reward = -3000 // (4 - tenpai_players_num)
        else :
            penalty = 0
            reaward = 0
        for i in range(4) :
            if players[i].is_tenpai : players[i].score(tenpai_reward)
            else : players[i].score(not_tenpai_penalty)
        # ゲーム終了判定
        self.is_over = self._check_game_is_over(players, players[self.rotations_num].is_tenpai)
        # 局の数等の変数操作
        self.counters_num += 1
        if players[self.rotations_num].is_tenpai is False :
            self.rotations_num += 1
            if self.rotations_num == 4 :
                self.rounds_num += 1
                self.rotations_num = 0


    # 流し満貫時の処理
    def proc_nagashi_mangan(self, players: List[Player]) -> None :
        for i in range(4) :
            if players[i].is_nagashi_mangan :
                if self.rotations_num == i :
                    players[i].score(12000)
                    for j in range(1,4) : players[(i+j)%4].score(-4000)
                else :
                    players[i].score(8000)
                    for j in range(1,4) :
                        if ((i+j)%4) == self.rotations_num : players[(i+j)%4].score(-4000)
                        else : players[(i+j)%4].score(-2000)
        # ゲーム終了判定
        self.is_over = self._check_game_is_over(players, players[self.rotations_num].is_tenpai)
        # 局の数等の変数操作
        self.counters_num += 1
        if players[self.rotations_num].is_tenpai is False :
            self.rotations_num += 1
            if self.rotations_num == 4 :
                self.rounds_num += 1
                self.rotations_num = 0


    # ゲーム終了判定
    def _check_game_is_over(self, players: List[Player], dealer_wins: bool ) -> bool :
        # トビ終了判定
        for i in range(4) :
            if players[i].score < 0 : return True
        # オーラス or 西場
        if (self.rounds_num == 1 and self.rotations_num == 3) or self.rounds_num == 2 :
            # 親がノーテン・和了ってない場合
            if dealer_wins is False :
                # 誰かが30000点以上なら終了
                for i in range(4) :
                    if players[i].score >= 30000 : return True
                # 次局が北場の場合終了
                if self.rounds_num == 2 and self.rotations_num == 3 : return True
            # 親がテンパイ・和了った場合
            else :
                # 親が30000点未満の場合続行
                if players[self.rotations_num].score < 30000 : return False
                # 親が30000点以上の場合
                else :
                    top = True
                    for i in range(4) :
                        if i == self.rotations_num : continue
                        elif players[self.rotations_num].score < players[i].score : top = False
                        elif players[self.rotations_num].score == players[i].score and (self.rotations_num > i) : top = False
                    # 親がトップなら終了
                    if top : return True
        # 北場なら終了 多分書かなくてもいいけど一応
        elif self.rounds_num == 3 : return True

        # どの終了条件も満たさない場合続行
        return False


    # 海底・河底かチェック
    def _check_player_wins_by_last_tile(self) -> None :
        if 136 - (self.i_wall + self.i_rinshan) == 14 : self.wins_by_last_tile = True

    # 嶺上開花かチェック
    def _check_player_wins_by_rinshan_kaihou(self) -> None :
        if self.kakan_flag or self.daiminkan_flag or self.ankan_flag and not(self.wins_by_ron) : self.wins_by_rinshan_kaihou = True


    # 槍槓かチェック
    def _check_player_wins_by_chankan(self) -> None :
        if self.kakan_flag and self.wins_by_ron : self.wins_by_chankan = True #チャンカンかどうか確認


    # 和了牌をセット
    def set_winning_tile(self, tile: int) -> None:
        if tile in Kinds.REDS : self.winning_tile = tile + 5
        else : self.winning_tile = tile


    # 大三元のパオをセット i_ap: 3枚目の三元牌を鳴いたプレイヤ, i_dp: 鳴かせたプレイヤ
    def set_pao_of_three_dragons(self, i_ap: int, i_dp: int) -> None :
        self.pao_info[0] = i_ap
        self.pao_info[1] = i_dp


    # 大四喜のパオをセット i_ap: 3枚目の三元牌を鳴いたプレイヤ, i_dp: 鳴かせたプレイヤ
    def set_pao_of_four_winds(self, i_ap: int, i_dp: int) -> None :
        self.pao_info[2] = i_ap
        self.pao_info[3] = i_dp


    # i_playerを1加算
    def increment_i_player(self) -> None :
        self.i_player = (self.i_player + 1) % 4


    # 全員に公開されている牌を追加
    def add_to_appearing_tiles(self, tile: int) -> None :
        if tile in Kinds.REDS :
            self.appearing_red_tiles[tile // 10] = True
            self.appearing_tiles[tile + 5] += 1
        else : self.appearing_tiles[tile] += 1


    # 通常の手の翻数の計算
    def _count_han_of_normal_hand(self, player: Player) -> None :
        hand = player.put_back_opened_hand()
        if four_concealed_triplets(player.has_stealed, self.wins_by_ron, hand, self.winning_tile) : self.yakuman += 1
        if four_concealed_triplets_of_single_tile_wait(player.has_stealed, self.winning_tile, hand) : self.yakuman += 1
        if four_kans(player.opened_hand) : self.yakuman += 1
        if all_honors(hand) : self.yakuman += 1
        if all_green(hand) : self.yakuman += 1
        if all_terminals(hand) : self.yakuman += 1
        if small_four_winds(hand) : self.yakuman += 1
        if big_four_winds(hand) : self.yakuman += 1
        if big_three_dragons(hand) : self.yakuman += 1
        if nine_gates(hand) and not(player.has_stealed) : self.yakuman += 1
        if self.yakuman == 0 :
            if player.has_declared_double_ready : self.han += 2
            if player.has_declared_ready : self.han += 1
            if player.one_shot : self.han += 1
            if not(player.has_stealed) and not(self.wins_by_ron) : self.han += 1
            if self.wins_by_rinshan_kaihou : self.han += 1
            if self.wins_by_last_tile : self.han += 1
            # if self.wins_by_haitei : self.han += 1
            # if self.wins_by_houtei : self.han += 1
            if self.wins_by_chankan : self.han += 1
            if self.tanyao(hand) : self.han += 1
            if self.prevailing_wind(hand, self.prevailing_wind) : self.han += 1
            if self.players_wind(hand, self.players_wind) : self.han += 1
            if self.white(hand) : self.han += 1
            if self.green(hand) : self.han += 1
            if self.red(hand) : self.han += 1
            if self.honroutou(hand) : self.han += 2
            if self.syousangen(hand) : self.han += 2
            if self.honitsu(hand) :
                if not(player.has_stealed) : self.han += 3
                else : self.han += 2
            if chinitsu(hand) :
                if not(player.has_stealed) : self.han += 6
                else : self.han += 5
            if player.red[0] : self.han += 1
            if player.red[1] : self.han += 1
            if player.red[2] : self.han += 1
            for i in range(5) :
                if self.dora_has_opened[i] :
                    self.han += hand[self.doras[i]]
                    if player.has_declared_ready or player.has_declared_double_ready : self.han += hand[self.uras[i]]
            if self.han < 13 : self._analyze_best_composition(player)
            else : self.yakuman = 1


    # 七対子手の翻数計算
    def _count_han_of_seven_pairs_hand(self, player: Player) -> None :
        hand = deepcopy(player.hand)
        if tsuuiisou(hand) : self.han += 13
        if self.han < 13 :
            self.han += 2
            if player.has_declared_double_ready : self.han += 2
            if player.has_declared_ready : self.han += 1
            if player.one_shot : self.han += 1
            if not(self.wins_by_ron) : self.han += 1
            if self.wins_by_rinshan_kaihou : self.han += 1
            if self.wins_by_last_tile : self.han += 1
            # if self.wins_by_haitei : self.han += 1
            # if self.wins_by_houtei : self.han += 1
            if self.wins_by_chankan : self.han += 1
            if tanyao(hand) : self.han += 1
            if chinitsu(hand) : self.han += 6
            if honitsu(hand) : self.han += 3
            if honroutou(hand) : self.han += 2
            if player.red[0] : self.han += 1
            if player.red[1] : self.han += 1
            if player.red[2] : self.han += 1
            for i in range(5) :
                if self.dora_has_opened[i] :
                    self.han += hand[self.doras[i]]
                    if player.has_declared_ready or player.has_declared_double_ready : self.han += hand[self.uras[i]]
            if self.han > 13 : self.han = 13
            self.fu = 25


    # 基本点の計算
    def _calc_basic_points(self, player: Player) -> int :
        self.han = 0
        if self.wins_by_tenhou : self.yakuman += 1
        if self.wins_by_chiihou : self.yakuman += 1
        player.calc_shanten_num_of_kokushi()
        player.calc_shanten_num_of_chiitoi()
        player.calc_shanten_num_of_normal()
        if player.shanten_num_of_normal == -1 : self._count_han_of_normal_hand(player)
        elif player.shanten_num_of_chiitoi == -1 : self._count_han_of_seven_pairs_hand(player)
        elif player.shanten_num_of_kokushi == -1 : self.yakuman += 1
        else :
            print("error : Game._calc_basic_points")

        basic_points = self.fu * (2 ** (self.han + 2))
        if self.yakuman > 0 : basic_points = self.yakuman * 8000
        elif self.han == 3 and self.fu >= 70 : basic_points = 2000
        elif self.han == 4 and self.fu >= 40 : basic_points = 2000
        elif self.han == 5 : basic_points = 2000
        elif self.han >= 6 and self.han < 8 : basic_points = 3000
        elif self.han >= 8 and self.han < 11 : basic_points = 4000
        elif self.han >= 11 and self.han < 13 : basic_points = 6000
        elif self.han >= 13 : basic_points = 8000

        return basic_points


    # 一番点数が高くなるような手牌構成を探す
    def _analyze_best_composition(self, player: Player) -> None :
        self.temp = [0] * 10
        self.i_temp = 0
        self.fu = 0
        self.han_temp = self.han
        hand = player.hand
        opened_hand = player.opened_hand
        for i in range(4) :
            if opened_hand[i*5] != 0 :
                self.temp[(i*2)] = opened_hand[i*5]
                self.temp[(i*2)+1] = opened_hand[(i*5)+1]
                self.i_temp += 2
            else : break
        for i in range(1,38) :
            if hand[i] == 0 : continue
            if hand[i] >= 2 :
                hand[i] -= 2
                self.temp[self.i_temp] = Block.TOITSU
                self.temp[self.i_temp+1] = i
                self.i_temp += 2
                self._pick_out_mentsu(player.has_stealed, hand);
                self.i_temp -= 2
                self.temp[self.i_temp] = 0
                self.temp[self.i_temp+1] = 0
                hand[i] += 2


    # 面子を抜き出す
    def _pick_out_mentsu(self, has_stealed: bool, hand: List[int]) -> None:
        for i in range(1,38) :
            if self.temp[9] != 0 :
                self._count_han(has_stealed)
                return
            if hand[i] == 0 : continue
            if hand[i] >= 3 :
                hand[i] -= 3
                if self.winning_tile == i and self.wins_by_ron and hand[i] == 0 : self.temp[self.i_temp] = Block.PON
                else : self.temp[self.i_temp] = Block.ANKO
                self.temp[self.i_temp + 1] = i
                self.i_temp += 2
                self._pick_out_mentsu(has_stealed, hand)
                self.i_temp -= 2
                self.temp[self.i_temp] = 0
                self.temp[self.i_temp + 1] = 0
                hand[i] += 3
            if i <= 27 and hand[i] > 0 and hand[i+1] > 0 and hand[i+2] > 0 :
                hand[i] -= 1
                hand[i+1] -= 1
                hand[i+2] -= 1
                self.temp[self.i_temp] = Block.SYUNTSU
                self.temp[self.i_temp+1] = i
                self.i_temp += 2
                self._pick_out_mentsu(has_stealed, hand)
                self.i_temp -= 2
                self.temp[self.i_temp] = 0
                self.temp[self.i_temp+1] = 0
                hand[i] += 1
                hand[i+1] += 1
                hand[i+2] += 1


    # 翻数を数える
    def _count_han(self, has_stealed: bool) -> None :
        han_temp = self.han_temp
        if no_points_hand(self.temp, self.winning_tile, self.prevailing_wind, self.players_wind) : han_temp += 1
        if terminal_or_honor_in_each_set(self.temp) :
            if has_stealed : han_temp += 1
            else : han_temp += 2
        if not(has_stealed) and one_set_of_identical_sequences(self.temp) : han_temp += 1
        if three_color_straight(self.temp) :
            if has_stealed : han_temp += 1
            else : han_temp += 2
        if straight(self.temp) :
            if has_stealed : han_temp += 1
            else : han_temp += 2
        if three_color_triplets(self.temp) : han_temp += 2
        if all_triplet_hand(self.temp) : han_temp += 2
        if three_closed_triplets(self.temp) : han_temp += 2
        if not(has_stealed) and two_sets_of_identical_sequences(self.temp) : han_temp += 3
        if terminal_in_each_set(self.temp) :
            if has_stealed : han_temp += 2
            else : han_temp += 3
        if three_kans(self.temp) : han_temp += 2
        if han_temp > self.han :
            self.han = han_temp
            self.fu = self._calc_fu(has_stealed)
        elif han_temp == self.han :
            fu_temp = self._calc_fu(has_stealed)
            if fu_temp > self.fu : self.fu = fu_temp

    def _calc_fu(self, has_stealed: bool) -> int :
        fu = 0
        if no_points_hand(self.temp, self.winning_tile, self.prevailing_wind, self.players_wind) :
            if self.wins_by_ron : return 30
            else : return 20
        fu = 20
        if not(has_stealed) and self.wins_by_ron : fu += 10
        elif not(self.wins_by_ron) : fu += 2
        for i in range(0, 10, 2) :
            if self.temp[i] == Block.SYUNTSU :
                if (self.temp[i+1] == self.winning_tile - 2 and self.temp[i+1] % 10 == 1) or \
                   (self.temp[i+1] == self.winning_tile and self.temp[i+1] % 10 == 7) or \
                   (self.temp[i+1] == self.winning_tile - 1) :
                    fu += 2
                    break
            elif self.temp[i] == Block.TOITSU :
                if self.temp[i+1] == self.winning_tile :
                    fu += 2
                    break
        for i in range(0, 10, 2) :
            if self.temp[i] == Block.PON :
                if self.temp[i+1] % 10 in [1,9] or self.temp[i+1] > 30 : fu += 4
                else : fu += 2
            elif self.temp[i] == Block.TOITSU :
                if self.temp[i+1] >= 35 or self.temp[i+1] == self.prevailing_wind : fu += 2
                if self.temp[i+1] == self.players_wind : fu += 2
            elif self.temp[i] in [Block.CHI, Block.SYUNTSU] : continue
            elif self.temp[i] == Block.ANKO :
                if self.temp[i+1] % 10 in [1,9] or self.temp[i+1] > 30 : fu += 8
                else : fu += 4
            elif self.temp[i] == Block.MINKAN :
                if self.temp[i+1] % 10 in [1,9] or self.temp[i+1] > 30 : fu += 16
                else : fu += 8
            elif self.temp[i] == Block.ANKAN :
                if self.temp[i+1] % 10 in [1,9] or self.temp[i+1] > 30 : fu += 32
                else : fu += 16
        if fu == 20 : fu = 30
        elif fu % 10 > 0 : fu = (fu + 10) - (fu % 10)
        return fu


    # 局の処理
    def _proc_subgame(players: List[Player], logger: Logger) -> None :
        # 配牌を配る
        for i in range(4) :
            for j in range(13) :
                tile = self.supply_next_tile()
                players[i].get_tile(tile)
                logger.add_to_first_hand(i, tile)

        # 配牌でテンパイかどうかチェック
        for i in range(4) : players[i].check_hand_is_ready()

        # ツモループ {
        while True :

            # 同順フリテン解消
            players[self.i_player].reset_same_turn_furiten()

            # 牌をツモる
            if self.has_stealed_flag is False :
                # 槓した場合は嶺上牌からツモる
                if self.kakan_flag or self.ankan_flag or self.daiminkan_flag : players[self.i_player].get_tile(self.supply_next_rinshan_tile())
                # そうでない場合は山からツモる
                else : players[self.i_player].get_tile(self.supply_next_tile())

                # 和了の判定
                self.win_flag = players[self.i_player].decide_win(self)

                # ツモ和了時の事前変数操作
                if self.win_flag :
                    players[self.i_player].wins = True
                    self.set_winning_tile(players[self.i_player].tsumo)
                    self._check_player_wins_by_rinshan_kaihou()
                    if self.wins_by_rinshan_kaihou is False : self._check_player_wins_by_last_tile()
                    break

                # 途中流局の判定
                if self.is_first_turn : self.is_abortive_draw = players[self.i_player].decide_kyushu_kyuhai()
                if self.is_abortive_draw : break
                if self._check_four_kans(players) : break

                # 一発を消す
                players[self.i_player].one_shot = False

            # 行動決定，tile:赤は(0,10,20)表示
            tile, ankan, kakan, ready, exchanged = players[self.i_player].decide_action(self, players)

            # 暗カンした時の処理
            if ankan :
                for i in range(4) : players[i].one_shot = False
                self._proc_ankan(tile)
                players[self.i_player].proc_ankan()
                continue
            # 加カンした時の処理
            if kakan :
                self._proc_kakan(tile)
                players[self.i_player].proc_kakan()
            # リーチした時の処理
            if ready :
                self.ready_flag = True
                self.deposits_num += 1
                players[self.i_player].call_ready(self.is_first_turn)

            # 牌を捨てる
            if not(self.kakan_flag) :
                # プレイヤが捨てる牌を決定，discarded_tile:赤は(0,10,20)表示
                discarded_tile = players[self.i_player].discard_tile()
                # 捨てられた牌を見えている牌に記録
                self.add_to_appearing_tiles(discarded_tile)
                # 鳴いた後に切った場合, 手出し牌に牌を記録
                if self.has_stealed_flag : players[self.i_player].add_to_discard_tiles_after_stealing(discarded_tile)
                self.has_stealed_flag = False
                if players[self.i_player].is_nagashi_mangan : players[self.i_player].check_nagashi_mangan()
                # 四風連打の判定
                if self.is_first_turn and (4 + self.i_player - self.rotations_num) % 4 == 3 :
                    if (discarded_tile in Kinds.WINDS) and (players[0].discarded_tiles[0] == players[1].discarded_tiles[0] == players[2].discarded_tiles[0] == players[3].discarded_tiles[0]) :
                        self.is_abortive_draw = True
                if self.is_abortive_draw : break

            # 四家立直の判定
            if (players[0].has_declared_ready or players[0].has_declared_double_ready) and \
               (players[1].has_declared_ready or players[1].has_declared_double_ready) and \
               (players[2].has_declared_ready or players[2].has_declared_double_ready) and \
               (players[3].has_declared_ready or players[3].has_declared_double_ready) :
                self.abortive_draw = True

            # 大ミンカンによるドラめくり ※タイミング複雑だけどここで合ってる
            if self.daiminkan_flag : self.open_new_dora()

            # 他家のロン和了
            for i in range(1,4) :
                i_winner = (self.i_player + i) % 4
                if players[i_winner].decide_win(self, tile) :
                    # 海底ずれるのでデクリメントする
                    if self.kakan_flag : self.i_rinshan -= 1
                    # リーチ宣言時のロンはリーチ不成立
                    if self.ready_flag :
                        self.deposits_num -= 1
                        self.ready_flag = False
                        players[self.i_player].score(1000)
                        players[i_winner].get_tile(tile)
                        self.win_flag = True
                        self.wins_by_ron = True

            # ロン和了時の事前変数処理
            if self.win_flag :
                self.set_winning_tile(tile)
                self._check_player_wins_by_last_tile()
                self._check_player_wins_by_chankan()
                break

            # 途中流局の場合break
            if self.abortive_draw : break

            # 槓の処理諸々 ※タイミング複雑だけど合ってる
            if self.ankan_flag :
                if self._check_four_kans(players) : break
            if self.kakan_flag :
                for i in range(4) : players[i].one_shot = False
                self.open_new_dora()
                continue
            if self.daiminkan_flag and self._check_four_kans(players) : break
            self.ankan_flag = False
            self.kakan_flag = False
            self.daiminkan_flag = False

            # 切った牌を他家のフリテン牌にセット
            for i in range(1,4) :
                op = (self.i_player + i) % 4
                if players[op].has_declared_ready or players[op].has_declared_double_ready : players[op].set_to_furiten_tiles(discarded_tile)
                else : players[op].set_to_same_turn_furiten_tiles(discarded_tile)

            # 副露
            # ポン，カン判定と処理
            for i in range(1,4) :
                i_ap = (self.i_player + i) % 4 #i_ap : index of action player
                pon, kan = players[i_ap].decide_pon_or_kan(self, players, tile)
                if (pon and kan) is False : continue
                else :
                    players[self.i_player].is_nagashi_mangan = False
                    for j in range(4) : players[j].one_shot = False
                    if pon :
                        players[i_ap].proc_pon(self, tile)
                        self.proc_pon(i_ap, tile)
                    elif kan :
                        players[i_ap].proc_daiminkan(tile)
                        self.proc_daiminkan(i_ap, tile)
                    break

            # チー判定と処理
            if (pon and kan) is False :
                i_ap = (self.i_player + 1) % 4 #i_ap : index of action player
                chii, tile1, tile2 = players[i_ap].decide_chii(self, players, tile)
                if chii :
                    players[self.i_player].is_nagashi_mangan = False
                    players[i_ap].proc_chii(tile, tile1, tile2)
                    self.proc_chii(tile, tile1, tile2)

            # プレイヤインデックスを加算
            self.increment_i_player()

            # 1順目かどうかの状態を更新
            if self.is_first_turn and self.i_player == 4 : self.is_first_turn = False

            # 局終了判定
            if 136 - (self.i_wall + self.i_rinshan) == 14 : break

        # } ツモループ

        # 三家和の判定 ※ほとんどならない三家和のために毎巡この処理するの嫌だからここに書いてる
        winners_num = 0
        for i in range(4) :
            if players[i].wins : winners_num += 1
        if winners_num == 3 :
            self.is_abortive_draw = True
            self.win_flag = False

        # 和了の処理
        if self.win_flag : self.proc_win(players)
        else :
            for i in range(4) : players[i].check_hand_is_ready()
            if self.is_abortive_draw : self.counters_num += 1
            # 流し満貫判定と処理
            elif ( players[0].is_nagashi_mangan or players[1].is_nagashi_mangan or players[2].is_nagashi_mangan or players[3].is_nagashi_mangan ) : self.proc_nagashi_mangan(players)
            # 和了，途中流局，流し満貫のどれでもなければ普通の流局処理
            else : self.proc_drawn_game(players)


    # 半荘の処理
    def proc_game(self) -> None :
        logger = Logger();
        players = [Player(i) for i in range(4)]

        while True :

            # 局
            self.init_subgame()
            for i in range(4) : players[i].init_subgame()
            self._proc_subgame(players, logger)

            # 半荘終了判定
            if self.is_over : break


