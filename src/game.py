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
四風連打で立直宣言時のリー棒の処理どうなる？

appearing_red_tilesの登録処理


ankan_flagとkakan_flagを廃止して next_tile_is_rinshan: bool と kakan_open_flagとかにする？
加槓ドラめくり
 - 加槓 -> 暗槓
 - 加槓 -> 加槓 （2回目の加槓で槍槓になると1回目の加槓の分は開かれるが2回目の分は開かれない）
 - 切った後（ロンする前）
"""


"""
TODO

四風連打で立直宣言時のリー棒の処理どうなる？

appearing_red_tilesの登録処理


ankan_flagとkakan_flagを廃止して next_tile_is_rinshan: bool と kakan_open_flagとかにする？
加槓ドラめくり
 - 加槓 -> 暗槓
 - 加槓 -> 加槓 （2回目の加槓で槍槓になると1回目の加槓の分は開かれるが2回目の分は開かれない）
 - 切った後（ロンする前）

四槓散了
 加槓，大明槓 : 切った牌が通ったら流局
 暗槓 : 切った牌が通ったらっぽい
"""


class Game :


    def __init__(self) :
        self.rounds_num = 0                            # 場 0:東場，1:南場，2:西場
        self.rotations_num = 0                         # 局 0:1局目 ... 3:4局目
        self.counters_num = 0                          # 積み棒の数
        self.deposits_num = 0                          # 供託の数
        self.prevailing_wind = 31 + self.rounds_num    # 場風にあたる牌番号
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
        self.steal_flag = False                        # 鳴き処理用
        self.dora_opens_flag = False                   # 加槓，大明槓による開槓flag．trueのままゲームが終わらず所定の処理までくるとドラを開けてfalseに戻る
        self.rinshan_draw_flag = False                 # 次のツモが嶺上牌であることを示すflag．trueのままドローフェーズまで来ると嶺上牌をツモってfalseに戻る


    # 局開始時の初期化
    def _init_subgame(self) -> None :
        self.is_abortive_draw = False                  # 途中流局になるとTrueになる
        self.is_first_turn = True                      # Trueの間は1巡目であることを示す

        self.prevailing_wind = 31 + self.rounds_num    # 場風にあたる牌番号
        self.is_abortive_draw = False                  # 途中流局になるとTrueになる
        self.is_first_turn = True                      # Trueの間は1巡目であることを示す
        self.pao_info = [-1] * 4

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
        self.rinshan_draw_flag = False
        self.dora_opens_flag = False

        self._set_doras()
        self._set_rinshan_tiles()


    # 赤有りの牌山を生成
    def _set_wall_containing_red(self) -> None :
        i, red = 0, False
        for j in range(1,38) :
            if j in TileType.BLANKS : continue
            if j in TileType.FIVES : red = True
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
            if dora_indicators[i] in TileType.REDS : indicator = dora_indicators[i] + 5
            else : indicator = dora_indicators[i]
            if indicator in TileType.NINES : doras[i] = indicator - 8
            elif indicator == 34 : doras[i] = 31
            elif indicator == 37 : doras[i] = 35
            else : doras[i] = indicator + 1

            # 裏ドラをセット
            if ura_indicators[i] in TileType.REDS : indicator = ura_indicators[i] + 5
            else : indicator = ura_indicators[i]
            if ura_indicator in TileType.NINES : uras[i] = ura_indicator - 8
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



    # 大明槓が行われた時の処理
    def _proc_daiminkan(self, tile: int, action_players_num: int) -> None :
        if tile in TileType.REDS : tile += 5
        self.appearing_tiles[tile] += 3
        self.is_first_turn = False
        self.i_player = action_players_num
        self.dora_opens_flag = True
        self.rinshan_draw_flag
        self.i_player = (4 + action_players_num - 1) % 4


    # ポンが行われた時の処理
    def _proc_pon(self, tile: int, action_players_num : int) -> None :
        if tile in TileType.REDS : tile += 5
        self.appearing_tiles[tile] += 2
        self.is_first_turn = False
        self.steal_flag = True
        self.i_player = (4 + action_players_num - 1) % 4


    # チーが行われた時の処理
    def _proc_chii(self, tile: int, tile1: int, tile2: int) -> None :
        if tile in TileType.REDS :
            tile += 5
            tile1 += 5
            tile2 += 5
        self.appearing_tiles[tile1] += 1
        self.appearing_tiles[tile2] += 1
        self.steal_flag = True
        self.is_first_turn = False


    # 点数計算前の準備
    def _preproc_calculating_basic_points(self, i_winner: int) -> None :
        # プレイヤの風牌を記録
        self.players_wind = 31 + (((i_winner + 4) - self.rounds_num) % 4)
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
        if self.dealer_wins : points = self.basic_points * 6
        else : points = self.basic_points * 4

        # 点数移動
        if self.wins_by_pao:
            players[self.i_player].score_points(-1 * (points // 2))
            players[liability_player].score_points(-1 * ((points // 2) + (300 * self.counters_num)))
            players[self.i_player].score_points(points)
        else :
            if points % 100 != 0 : points += int(100 - (points % 100)) # 100の位で切り上げ
            players[self.i_player].score_points(-1 * (points + (300 * self.counters_num)))
            players[i_winner].score_points(points)


    # ツモ和了の処理
    def _proc_tsumo(self, players: List[Player], i_winner: int) -> int :
        if self.wins_by_pao:
            if not(self.dealer_wins) : points = self.basic_points * 4
            else : points = self.basic_points * 6
            players[liability_player].score_points(-1 * (points + (300 * self.counters_num)))
            players[self.i_player].score_points(points)
        else :
            if self.dealer_wins :
                points = self.basic_points * 2
                if points % 100 != 0 : points += (100 - (points % 100))
                for i in range(1,4) : players[(i_winner + i) % 4].score_points(-1 * (points + (100 * self.counters_num)))
                players[i_winner].score_points(points * 3)
            else :
                score_which_dealer_pay = self.basic_points * 2
                if score_which_dealer_pay % 100 != 0 : score_which_dealer_pay += (100 - (score_which_dealer_pay % 100))
                score_which_child_pay = self.basic_points
                if score_which_child_pay % 100 != 0 : score_which_child_pay += (100 - (score_which_child_pay % 100))
                for i in range(1,4) :
                    i_payer = (i_winner + i) % 4
                    if i_payer != self.rotations_num :
                        players[i_payer].score_points(-1 * (score_which_child_pay + (100 * self.counters_num)))
                        players[i_winner].score_points(score_which_child_pay)
                    else :
                        players[i_payer].score_points(-1 * (score_which_dealer_pay + (100 * self.counters_num)))
                        players[self.i_player].score_points(score_which_dealer_pay)


    # 和了時の処理
    def _proc_win(self, players: List[Player]) -> None :
        counters_num_temp = self.counters_num
        # ツモった人，最後に牌を切った人から順に和了を見ていく．※ 複数人の和了の可能性があるので全員順番にチェックする必要がある．
        for i in range(4) :
            i_winner = (self.i_player + i) % 4
            if players[i_winner].wins :
                self._preproc_calculating_basic_points()
                self.basic_points = self._calculate_basic_points(players[self.i_player])
                if self.wins_by_ron : self._proc_ron(i_winner)
                else : self._proc_tsumo(i_winner)
                players[i_winner].score_points(300 * self.counters_num)
                players[i_winner].score_points(1000 * self.deposits_num)
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
    def _proc_drawn_game(self, players: List[Player]) -> None :
        tenpai_players_num = 0
        for i in range(4) :
            if players[i].is_ready : tenpai_players_num += 1
        if tenpai_players_num != 0 and tenpai_players_num != 4 :
            not_tenpai_penalty = 3000 // tenpai_players_num
            tenpai_reward = -3000 // (4 - tenpai_players_num)
        else :
            penalty = 0
            reaward = 0
        for i in range(4) :
            if players[i].is_ready : players[i].score_points(tenpai_reward)
            else : players[i].score_points(not_tenpai_penalty)
        # ゲーム終了判定
        self.is_over = self._check_game_is_over(players, players[self.rotations_num].is_ready)
        # 局の数等の変数操作
        self.counters_num += 1
        if players[self.rotations_num].is_ready is False :
            self.rotations_num += 1
            if self.rotations_num == 4 :
                self.rounds_num += 1
                self.rotations_num = 0


    # 流し満貫時の処理
    def _proc_nagashi_mangan(self, players: List[Player]) -> None :
        for i in range(4) :
            if players[i].is_nagashi_mangan :
                if self.rotations_num == i :
                    players[i].score_points(12000)
                    for j in range(1,4) : players[(i+j)%4].score_points(-4000)
                else :
                    players[i].score_points(8000)
                    for j in range(1,4) :
                        if ((i+j)%4) == self.rotations_num : players[(i+j)%4].score_points(-4000)
                        else : players[(i+j)%4].score_points(-2000)
        # ゲーム終了判定
        self.is_over = self._check_game_is_over(players, players[self.rotations_num].is_ready)
        # 局の数等の変数操作
        self.counters_num += 1
        if players[self.rotations_num].is_ready is False :
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


    # 和了牌をセット
    def set_winning_tile(self, tile: int) -> None:
        if tile in TileType.REDS : self.winning_tile = tile + 5
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
        if tile in TileType.REDS :
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
            if self.wins_by_chankan : self.han += 1
            if all_simples(hand) : self.han += 1
            if prevailing_wind(hand, self.prevailing_wind) : self.han += 1
            if players_wind(hand, self.players_wind) : self.han += 1
            if white_dragon(hand) : self.han += 1
            if green_dragon(hand) : self.han += 1
            if red_dragon(hand) : self.han += 1
            if all_terminals_and_honors(hand) : self.han += 2
            if little_three_dragons(hand) : self.han += 2
            if half_flush(hand) :
                if not(player.has_stealed) : self.han += 3
                else : self.han += 2
            if flush(hand) :
                if not(player.has_stealed) : self.han += 6
                else : self.han += 5
            if player.reds[0] : self.han += 1
            if player.reds[1] : self.han += 1
            if player.reds[2] : self.han += 1
            for i in range(5) :
                if self.dora_has_opened[i] :
                    self.han += hand[self.doras[i]]
                    if player.has_declared_ready or player.has_declared_double_ready :
                        self.han += hand[self.uras[i]]
            if self.han < 13 :
                self._analyze_best_composition(player)
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
            if self.wins_by_chankan : self.han += 1
            if all_simples(hand) : self.han += 1
            if flush(hand) : self.han += 6
            if half_flush(hand) : self.han += 3
            if all_terminals_and_honors(hand) : self.han += 2
            if player.reds[0] : self.han += 1
            if player.reds[1] : self.han += 1
            if player.reds[2] : self.han += 1
            for i in range(5) :
                if self.dora_has_opened[i] :
                    self.han += hand[self.doras[i]]
                    if player.has_declared_ready or player.has_declared_double_ready : self.han += hand[self.uras[i]]
            if self.han > 13 : self.han = 13
            self.fu = 25


    # 基本点の計算
    def _calculate_basic_points(self, player: Player) -> int :
        self.han = 0
        if self.wins_by_tenhou : self.yakuman += 1
        if self.wins_by_chiihou : self.yakuman += 1
        player.calculate_shanten_num_of_kokushi()
        player.calculate_shanten_num_of_chiitoi()
        player.calculate_shanten_num_of_normal()
        if player.shanten_num_of_normal == -1 : self._count_han_of_normal_hand(player)
        elif player.shanten_num_of_chiitoi == -1 : self._count_han_of_seven_pairs_hand(player)
        elif player.shanten_num_of_kokushi == -1 : self.yakuman += 1
        else :
            print("error : Game._calculate_basic_points")

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
                self.temp[self.i_temp] = Block.PAIR
                self.temp[self.i_temp+1] = i
                self.i_temp += 2
                self._pick_out_mentsu(player.has_stealed, hand);
                self.i_temp -= 2
                self.temp[self.i_temp] = 0
                self.temp[self.i_temp+1] = 0
                hand[i] += 2


    # 面子を抜き出す
    ## 和了が確定してからしか呼ばれないので高速化のためにPlayer._pick_out_mentsu()でやらなくていい部分を省いている．別物.
    def _pick_out_mentsu(self, has_stealed: bool, hand: List[int]) -> None:
        for i in range(1,38) :
            if self.temp[9] != 0 :
                self._count_han(has_stealed)
                return
            if hand[i] == 0 : continue
            if hand[i] >= 3 :
                hand[i] -= 3
                if self.winning_tile == i and self.wins_by_ron and hand[i] == 0 : self.temp[self.i_temp] = Block.CLOSED_TRIPLET
                else : self.temp[self.i_temp] = Block.CLOSED_TRIPLET
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
                self.temp[self.i_temp] = Block.CLOSED_RUN
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
            self.fu = self._calculate_fu(has_stealed)
        elif han_temp == self.han :
            fu_temp = self._calculate_fu(has_stealed)
            if fu_temp > self.fu : self.fu = fu_temp


    # 符計算
    def _calculate_fu(self, has_stealed: bool) -> int :
        fu = 0
        if no_points_hand(self.temp, self.winning_tile, self.prevailing_wind, self.players_wind) :
            if self.wins_by_ron : return 30
            else : return 20
        fu = 20
        if not(has_stealed) and self.wins_by_ron : fu += 10
        elif not(self.wins_by_ron) : fu += 2
        for i in range(0, 10, 2) :
            if self.temp[i] == Block.CLOSED_RUN :
                if (self.temp[i+1] == self.winning_tile - 2 and self.temp[i+1] % 10 == 1) or \
                   (self.temp[i+1] == self.winning_tile and self.temp[i+1] % 10 == 7) or \
                   (self.temp[i+1] == self.winning_tile - 1) :
                    fu += 2
                    break
            elif self.temp[i] == Block.PAIR :
                if self.temp[i+1] == self.winning_tile :
                    fu += 2
                    break
        for i in range(0, 10, 2) :
            if self.temp[i] == Block.OPENED_TRIPLET :
                if self.temp[i+1] % 10 in [1,9] or self.temp[i+1] > 30 : fu += 4
                else : fu += 2
            elif self.temp[i] == Block.PAIR :
                if self.temp[i+1] >= 35 or self.temp[i+1] == self.prevailing_wind : fu += 2
                if self.temp[i+1] == self.players_wind : fu += 2
            elif self.temp[i] in Block.RUNS : continue
            elif self.temp[i] == Block.CLOSED_TRIPLET :
                if self.temp[i+1] % 10 in [1,9] or self.temp[i+1] > 30 : fu += 8
                else : fu += 4
            elif self.temp[i] == Block.OPENED_KAN :
                if self.temp[i+1] % 10 in [1,9] or self.temp[i+1] > 30 : fu += 16
                else : fu += 8
            elif self.temp[i] == Block.CLOSED_KAN :
                if self.temp[i+1] % 10 in [1,9] or self.temp[i+1] > 30 : fu += 32
                else : fu += 16
        if fu == 20 : fu = 30
        elif fu % 10 > 0 : fu = (fu + 10) - (fu % 10)
        return fu


    # ドローフェーズの処理
    def _proc_draw_phase(self, players: List[Player]) -> None :
        # ポン，チーした場合はスキップ
        if self.steal_flag : return

        # 槓した場合は嶺上牌から，そうでない場合は山からツモる
        if self.rinshan_draw_flag : players[self.i_player].add_tile_to_hand(self.supply_next_rinshan_tile())
        else : players[self.i_player].add_tile_to_hand(self.supply_next_tile())

        # 和了の判定
        self.win_flag = players[self.i_player].decide_win(self)

        # ツモ和了時の事前変数操作
        if self.win_flag :
            players[self.i_player].wins = True
            self.set_winning_tile(players[self.i_player].last_added_tile)
            if self.rinshan_draw_flag : self.wins_by_rinshan_kaihou = True
            if self.wins_by_rinshan_kaihou is False : self._check_player_wins_by_last_tile() # 嶺上と河底は重複しない

        # 嶺上flagを元に戻す
        self.rinshan_draw_flag = False


    # 立直の処理
    def _proc_ready(self, player: Player) -> None :
        self.ready_flag = True
        self.deposits_num += 1
        player.declare_ready(self.is_first_turn)


    # 暗槓が行われた時の処理
    def _proc_ankan(self, tile: int, players: List[Player]) -> None :
        # 直前の行動が加槓だった場合このタイミングでドラが開く
        if self.dora_opens_flag :
            self.open_new_dora()
            self.dora_opens_flag = False

        if tile in TileType.REDS : tile += 5
        self.appearing_tiles[tile] += 4
        self.is_first_turn = False
        self.open_new_dora()
        self.rinshan_draw_flag = True
        for i in range(4) : players[i].one_shot = False
        players[self.i_player].proc_ankan()

        return


    # 加槓が行われた時の処理
    def _proc_kakan(self, tile: int, players: List[Player]) -> None :
        if tile in TileType.REDS : tile += 5
        self.appearing_tiles[tile] += 1
        self.rinshan_draw_flag = True
        self.dora_opens_flag = True
        for i in range(4) : players[i].one_shot = False
        players[self.i_player].proc_kakan()

        return


    # アクションフェーズの処理
    def _proc_action_phase(self, players: List[Player]) -> None :
        # プレイヤの行動決定，tile:赤は(0,10,20)表示
        tile, exchanged, ready, ankan, kakan, kyushu = players[self.i_player].decide_action(self, players)

        if ready : self._proc_ready(players[self.i_player])
        elif anakn : self._proc_ankan(tile, players)
        elif kakan :
            # 直前の行動が加槓だった場合このタイミングでドラが開く
            if self.dora_opens_flag :
                self.open_new_dora()
                self.dora_opens_flag = False
            # 槍槓用ロンフェーズ
            self._proc_ron_phase(tile, players, True)
            if self.win_flag : return
            self._prock_kakan(tile, players)
        elif kyushu : self.is_abortive_draw = True

        return


    # 打牌フェーズ
    def _proc_discard_phase(self, player: Player) -> None :
        # プレイヤが捨てる牌を決定，discarded_tile:赤は(0,10,20)表示
        discarded_tile = player.discard_tile()
        # 捨てられた牌を見えている牌に記録
        self.add_to_appearing_tiles(discarded_tile)
        # 鳴いた後に切った場合, 手出し牌に牌を記録
        if self.steal_flag : player.add_to_discard_tiles_after_stealing(discarded_tile)
        self.steal_flag = False
        if player.is_nagashi_mangan : players[self.i_player].check_nagashi_mangan()


    # ロンフェーズ
    def _proc_ron_phase(self, players: List[Player], discarded_tile: int, chankan: bool = False) -> None :
        winners_num = 0
        for i in range(1,4) :
            i_winner = (self.i_player + i) % 4
            if players[i_winner].decide_win(self, discarded_tile, chankan) :
                # リーチ宣言時のロンはリーチ不成立
                if self.ready_flag :
                    self.ready_flag = False
                    # リー棒返却
                    self.deposits_num -= 1
                    players[self.i_player].score_points(1000)

                # 和了人数をincrement
                winners_num += 1

                # 切られた牌を手牌に加える
                players[i_winner].add_tile_to_hand(discarded_tile)

                # 和了牌を記録．平和判定とかに使う．
                self.set_winning_tile(tile)

                # 槍槓があるかどうかを記録
                if chankan : self.wins_by_chankan = True

                # 河底のチェック
                self._check_player_wins_by_last_tile()

                # ロン和了フラグを立てる
                self.win_flag = True
                self.wins_by_ron = True
                players[i_winner].wins = True

        # 三家和判定
        if winners_num == 3 :
            self.is_abortive_draw = True
            self.win_flag = False


    # 途中流局（四風連打，四家立直，四槓散了）の判定
    def _check_game_is_abortive_draw(self, players) -> None :
        #  四風連打の判定
        if self.is_first_turn and (4 + self.i_player - self.rotations_num) % 4 == 3 :
            if (discarded_tile in TileType.WINDS) and (players[0].discarded_tiles[0] == players[1].discarded_tiles[0] == players[2].discarded_tiles[0] == players[3].discarded_tiles[0]) :
                self.is_abortive_draw = True

        #  四家立直の判定
        if (players[0].has_declared_ready or players[0].has_declared_double_ready) and \
            (players[1].has_declared_ready or players[1].has_declared_double_ready) and \
            (players[2].has_declared_ready or players[2].has_declared_double_ready) and \
            (players[3].has_declared_ready or players[3].has_declared_double_ready) :
            self.is_abortive_draw = True

        # 四槓散了判定．四槓散了は暗槓，加槓，大明槓どの場合でも牌がきられて通ったタイミングで判定される
        kans_num = 0
        for i in range(4) :
            if players[i].kans_num == 4 : return False # 一人で4回槓しているのは流局にならない
            kans_num += players[i].kans_num
        if kans_num == 4 :
            self.is_abortive_draw = True


    # 副露フェーズ
    def _proc_steal_phase(self, players: List[Player], discarded_tile: int) -> None :
        # ポン，カン判定と処理
        for i in range(1,4) :
            i_ap = (self.i_player + i) % 4 #i_ap : index of action player
            pon, kan = players[i_ap].decide_pon_or_kan(self, players, discarded_tile)
            if (pon and kan) is False : continue
            else :
                players[self.i_player].is_nagashi_mangan = False
                for j in range(4) : players[j].one_shot = False
                if pon :
                    players[i_ap].proc_pon(self, discarded_tile)
                    self._proc_pon(i_ap, discarded_tile)
                elif kan :
                    players[i_ap].proc_daiminkan(discarded_tile)
                    self._proc_daiminkan(i_ap, discarded_tile)
                break

        # チー判定と処理
        if (pon and kan) is False :
            i_ap = (self.i_player + 1) % 4 #i_ap : index of action player
            chii, tile1, tile2 = players[i_ap].decide_chii(self, players, tile)
            if chii :
                players[self.i_player].is_nagashi_mangan = False
                players[i_ap].proc_chii(tile, tile1, tile2)
                self.proc_chii(tile, tile1, tile2)


    # 局の処理
    def _proc_subgame(self, players: List[Player], logger: Logger) -> None :
        # 配牌を配る
        for i in range(4) :
            for j in range(13) :
                tile = self.supply_next_tile()
                players[i].add_tile_to_hand(tile)
                logger.add_to_first_hand(i, tile)

        # 配牌でテンパイかどうかチェック
        ### これなんの為？
        for i in range(4) : players[i].check_hand_is_ready()

        # ツモループ {
        while True :

            # 同順フリテン解消
            players[self.i_player].reset_same_turn_furiten()

            # ツモフェーズ
            self._proc_draw_phase(players[self.i_player])
            # ツモ和了ならループから抜ける
            if self.win_flag : break
            # 一発の権利がなくなる
            players[self.i_player].has_right_to_one_shot = False

            # アクションフェーズ
            self._proc_action_phase(players)

            # 槍槓ロンならループから抜ける
            if self.win_flag : break
            # 暗槓，加槓の場合，次のツモにスキップ
            if self.rinshan_draw_flag : continue
            # 九種九牌用
            if self.is_abortive_draw : break

            # 打牌フェーズ
            discarded_tile = self._proc_discard_phase(players[self.i_player])

            # 大明槓，加槓した場合牌を切った後にドラをめくる
            if self.dora_opens_flag :
                self._open_new_dora()
                self.dora_opens_flag = False

            # ロンフェーズ
            self._proc_ron_phase(players, discarded_tile)
            # ロン和了ならループから抜ける
            if self.win_flag : break

            # 途中流局の判定
            self._check_game_is_abortive_draw(players)
            if self.is_abortive_draw : break

            # 切った牌を他家のフリテン牌にセット
            for i in range(1,4) :
                op = (self.i_player + i) % 4
                if players[op].has_declared_ready or players[op].has_declared_double_ready : players[op].set_to_furiten_tiles(discarded_tile)
                else : players[op].set_to_same_turn_furiten_tiles(discarded_tile)

            # 副露フェーズ
            self._proc_steal_phase(players)

            # プレイヤインデックスを加算
            self.increment_i_player()

            # 1巡目かどうかの状態を更新
            if self.is_first_turn and self.i_player == 4 : self.is_first_turn = False

            # 通常流局判定
            if 136 - (self.i_wall + self.i_rinshan) == 14 : break

        # } ツモループ

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
            self._init_subgame()
            for i in range(4) : players[i].init_subgame()
            self._proc_subgame(players, logger)

            # 半荘終了判定
            if self.is_over : break


