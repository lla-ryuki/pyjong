#std
import random
from typing import List

# 3rd

# ours
from pymod.player import Player
from pymod.shanten import ShantenNumCalculator
from pymod.logger import Logger
from pymod.mytypes import TileType, BlockType
from pymod.yaku import *
from pymod.yakuman import *


class Game :
    def __init__(self, action=None) :
        self.players = [Player(i) for i in range(4)]
        self.action = action
        self.logger = Logger(is_logging=True);
        self.shanten_calculator = ShantenNumCalculator()
        self.rounds_num = 0                            # 場 0:東場，1:南場，2:西場
        self.rotations_num = 0                         # 局 0:1局目 ... 3:4局目
        self.counters_num = 0                          # 積み棒の数
        self.deposits_num = 0                          # 供託の数
        self.is_over = False                           # Trueになると半荘終了



    # 局開始時の初期化
    def init_subgame(self) -> None :
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

        # 牌山をセット
        self.set_rinshan_tiles()
        self.set_wall()
        self.set_doras()


    # 赤有りの牌山を生成
    def set_wall(self) -> None :
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


    # 新しいドラを開く
    def open_new_dora(self) -> None :
        for i in range(5) :
            if self.dora_has_opened[i] is False :
                self.dora_has_opened[i] = True
                self.appearing_tiles[self.dora_indicators[i]] += 1
                break


    #ドラと裏ドラをセット
    def set_doras(self) -> None :
        # ドラ表示牌, 裏ドラ表示牌をセット
        self.dora_indicators = [self.wall[i] for i in range(130, 121, -2)]
        self.ura_indicators = [self.wall[i] for i in range(131, 122, -2)]

        for i in range(5) :
            # ドラをセット
            if self.dora_indicators[i] in TileType.REDS : indicator = self.dora_indicators[i] + 5
            else : indicator = self.dora_indicators[i]
            if indicator in TileType.NINES : self.doras[i] = indicator - 8
            elif indicator == 34 : self.doras[i] = 31
            elif indicator == 37 : self.doras[i] = 35
            else : self.doras[i] = indicator + 1

            # 裏ドラをセット
            if self.ura_indicators[i] in TileType.REDS : ura_indicator = self.ura_indicators[i] + 5
            else : ura_indicator = self.ura_indicators[i]
            if ura_indicator in TileType.NINES : self.uras[i] = ura_indicator - 8
            elif ura_indicator == 34 : self.uras[i] = 31
            elif ura_indicator == 37 : self.uras[i] = 35
            else : self.uras[i] = ura_indicator + 1

        self.open_new_dora()


    # 嶺上牌をセット
    def set_rinshan_tiles(self) -> None :
        self.rinshan_tiles = [self.wall[134], self.wall[135], self.wall[132], self.wall[133]]


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
    def proc_daiminkan(self, i_ap:int, tile:int) -> None :
        pos = (4 + self.i_player - i_ap) % 4  # 鳴いた人（i_ap)から見た切った人の場所．pos = 1:下家, 2:対面, 3上家
        self.players[i_ap].proc_daiminkan(tile, pos)
        self.logger.register_daiminkan(i_ap, tile, pos)

        if tile in TileType.REDS : tile += 5
        self.appearing_tiles[tile] += 3
        self.is_first_turn = False
        self.dora_opens_flag = True
        self.rinshan_draw_flag = True
        self.i_player = (4 + i_ap - 1) % 4


    # ポンが行われた時の処理
    def proc_pon(self, i_ap:int, tile:int) -> None :
        pos = (4 + self.i_player - i_ap) % 4  # 鳴いた人（i_ap)から見た切った人の場所．pos = 1:下家, 2:対面, 3上家
        pao = self.players[i_ap].proc_pon(self, tile, pos)
        if pao > -1 : self.set_pao(pao, i_ap, self.i_player)
        self.logger.register_pon(i_ap, tile, pos)

        if tile in TileType.REDS : tile += 5
        self.appearing_tiles[tile] += 2
        self.is_first_turn = False
        self.steal_flag = True
        self.i_player = (4 + i_ap - 1) % 4


    # チーが行われた時の処理
    def proc_chii(self, i_ap:int, tile:int, tile1:int, tile2:int) -> None :
        self.players[i_ap].proc_chii(tile, tile1, tile2)
        self.logger.register_chii(i_ap, tile, tile1, tile2)

        if tile in TileType.REDS : tile += 5
        elif tile1 in TileType.REDS : tile1 += 5
        elif tile2 in TileType.REDS : tile2 += 5
        self.appearing_tiles[tile1] += 1
        self.appearing_tiles[tile2] += 1
        self.is_first_turn = False
        self.steal_flag = True


    # 点数計算前の準備
    def preproc_calculating_basic_points(self, i_winner:int) -> None :
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
    def proc_ron(self, i_winner:int) -> int :
        # 基本点から得点を算出
        if self.dealer_wins : points = self.basic_points * 6
        else : points = self.basic_points * 4

        # 点数移動
        if self.wins_by_pao:
            self.players[self.i_player].score_points(-1 * (points // 2))
            self.players[liability_player].score_points(-1 * ((points // 2) + (300 * self.counters_num)))
            self.players[self.i_player].score_points(points)
        else :
            if points % 100 != 0 : points += int(100 - (points % 100)) # 100の位で切り上げ
            self.players[self.i_player].score_points(-1 * (points + (300 * self.counters_num)))
            self.players[i_winner].score_points(points)


    # ツモ和了の処理
    def proc_tsumo(self, i_winner:int) -> int :
        if self.wins_by_pao:
            if not(self.dealer_wins) : points = self.basic_points * 4
            else : points = self.basic_points * 6
            self.players[liability_player].score_points(-1 * (points + (300 * self.counters_num)))
            self.players[self.i_player].score_points(points)
        else :
            if self.dealer_wins :
                points = self.basic_points * 2
                if points % 100 != 0 : points += (100 - (points % 100))
                for i in range(1,4) : self.players[(i_winner + i) % 4].score_points(-1 * (points + (100 * self.counters_num)))
                self.players[i_winner].score_points(points * 3)
            else :
                points_dealer_pays = self.basic_points * 2
                if points_dealer_pays % 100 != 0 : points_dealer_pays += (100 - (points_dealer_pays % 100))
                points_child_pays = self.basic_points
                if points_child_pays % 100 != 0 : points_child_pays += (100 - (points_child_pays % 100))
                for i in range(1,4) :
                    i_payer = (i_winner + i) % 4
                    if i_payer != self.rotations_num :
                        self.players[i_payer].score_points(-1 * (points_child_pays + (100 * self.counters_num)))
                        self.players[i_winner].score_points(points_child_pays)
                    else :
                        self.players[i_payer].score_points(-1 * (points_dealer_pays + (100 * self.counters_num)))
                        self.players[self.i_player].score_points(points_dealer_pays)


    # 和了時の処理
    def proc_win(self) -> None :
        counters_num_temp = self.counters_num
        # ツモった人，最後に牌を切った人から順に和了を見ていく．※ 複数人の和了の可能性があるので全員順番にチェックする必要がある．
        for i in range(4) :
            i_winner = (self.i_player + i) % 4
            if self.players[i_winner].wins :
                self.preproc_calculating_basic_points(i_winner)
                self.basic_points = self.calculate_basic_points(self.players[self.i_player])
                if self.wins_by_ron : self.proc_ron(i_winner)
                else : self.proc_tsumo(i_winner)
                self.players[i_winner].score_points(300 * self.counters_num)
                self.players[i_winner].score_points(1000 * self.deposits_num)
                self.counters_num, self.deposits_num = 0, 0
                if i == 0 : break
        # ゲーム終了判定
        self.is_over = self.check_game_is_over(self.players[self.rotations_num].wins)
        # 局の数等の変数操作
        if self.players[self.rotations_num].wins : self.counters_num += 1
        else :
            self.counters_num = 0
            self.rotations_num += 1
            if self.rotations_num == 4 :
                self.rounds_num += 1
                self.rotations_num = 0


    # 流局時の処理
    ####
    def proc_drawn_game(self) -> None :
        tenpai_players_num = 0
        for i in range(4) :
            if self.players[i].is_ready : tenpai_players_num += 1
        if tenpai_players_num != 0 and tenpai_players_num != 4 :
            penalty = 3000 // tenpai_players_num
            reward = -3000 // (4 - tenpai_players_num)
        else :
            penalty = 0
            reaward = 0
        for i in range(4) :
            if self.players[i].is_ready : self.players[i].score_points(reward)
            else : self.players[i].score_points(penalty)
        # ゲーム終了判定
        self.is_over = self.check_game_is_over(self.players[self.rotations_num].is_ready)
        # 局の数等の変数操作
        self.counters_num += 1
        if self.players[self.rotations_num].is_ready is False :
            self.rotations_num += 1
            if self.rotations_num == 4 :
                self.rounds_num += 1
                self.rotations_num = 0


    # 流し満貫時の処理
    def proc_nagashi_mangan(self) -> None :
        for i in range(4) :
            if self.players[i].is_nagashi_mangan :
                if self.rotations_num == i :
                    self.players[i].score_points(12000)
                    for j in range(1,4) : self.players[(i+j)%4].score_points(-4000)
                else :
                    self.players[i].score_points(8000)
                    for j in range(1,4) :
                        if ((i+j)%4) == self.rotations_num : self.players[(i+j)%4].score_points(-4000)
                        else : self.players[(i+j)%4].score_points(-2000)
        # ゲーム終了判定
        self.is_over = self.check_game_is_over(self.players[self.rotations_num].is_ready)
        # 局の数等の変数操作
        self.counters_num += 1
        if self.players[self.rotations_num].is_ready is False :
            self.rotations_num += 1
            if self.rotations_num == 4 :
                self.rounds_num += 1
                self.rotations_num = 0


    # ゲーム終了判定
    def check_game_is_over(self, dealer_wins:bool) -> bool :
        # トビ終了判定
        for i in range(4) :
            if self.players[i].score < 0 : return True
        # オーラス or 西場
        if (self.rounds_num == 1 and self.rotations_num == 3) or self.rounds_num == 2 :
            # 親がノーテン・和了ってない場合
            if dealer_wins is False :
                # 誰かが30000点以上なら終了
                for i in range(4) :
                    if self.players[i].score >= 30000 : return True
                # 次局が北場の場合終了
                if self.rounds_num == 2 and self.rotations_num == 3 : return True
            # 親がテンパイ・和了った場合
            else :
                # 親が30000点未満の場合続行
                if self.players[self.rotations_num].score < 30000 : return False
                # 親が30000点以上の場合
                else :
                    top = True
                    for i in range(4) :
                        if i == self.rotations_num : continue
                        elif self.players[self.rotations_num].score < self.players[i].score : top = False
                        elif self.players[self.rotations_num].score == self.players[i].score and (self.rotations_num > i) : top = False
                    # 親がトップなら終了
                    if top : return True
        # 北場なら終了 多分書かなくてもいいけど一応
        elif self.rounds_num == 3 : return True

        # どの終了条件も満たさない場合続行
        return False


    # 海底・河底かチェックして記録
    def check_player_wins_by_last_tile(self) -> None :
        if self.is_last_tile() : self.wins_by_last_tile = True

    # 記録はせずに海底・河底かだけ返す
    def is_last_tile(self) -> None :
        if 136 - (self.i_wall + self.i_rinshan) == 14 : return True


    # 和了牌をセット
    def set_winning_tile(self, tile:int) -> None:
        if tile in TileType.REDS : self.winning_tile = tile + 5
        else : self.winning_tile = tile


    # パオをセット i_ap: 最後の牌を鳴いたプレイヤ, i_dp: 鳴かせたプレイヤ
    def set_pao(self, pao:int, i_ap:int, i_dp:int) -> None :
        self.pao_info[pao*2] = i_ap
        self.pao_info[pao*2+1] = i_dp


    # i_playerを1加算
    def increment_i_player(self) -> None :
        self.i_player = (self.i_player + 1) % 4


    # 全員に公開されている牌を追加
    def add_to_appearing_tiles(self, tile:int) -> None :
        if tile in TileType.REDS :
            self.appearing_red_tiles[tile // 10] = True
            self.appearing_tiles[tile + 5] += 1
        else : self.appearing_tiles[tile] += 1


    # 通常の手の翻数の計算
    def count_han_of_normal_hand(self, player:Player) -> None :
        hand = player.put_back_opened_hand()
        if four_closed_triplets(player.has_stealed, self.wins_by_ron, hand, self.winning_tile) : self.yakuman += 1
        if four_closed_triplets_of_single_tile_wait(player.has_stealed, self.winning_tile, hand) : self.yakuman += 1
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
            if player.has_right_to_one_shot : self.han += 1
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
            if player.reds[0] or player.opened_reds[0] : self.han += 1
            if player.reds[1] or player.opened_reds[1] : self.han += 1
            if player.reds[2] or player.opened_reds[2] : self.han += 1
            for i in range(5) :
                if self.dora_has_opened[i] :
                    self.han += hand[self.doras[i]]
                    if player.has_declared_ready or player.has_declared_double_ready :
                        self.han += hand[self.uras[i]]
            if self.han < 13 :
                self.analyze_best_composition(player)
            else : self.yakuman = 1


    # 七対子手の翻数計算
    def count_han_of_seven_pairs_hand(self, player:Player) -> None :
        hand = player.hand[:]
        if all_honors(hand) : self.han += 13
        if self.han < 13 :
            self.han += 2
            if player.has_declared_double_ready : self.han += 2
            if player.has_declared_ready : self.han += 1
            if player.has_right_to_one_shot : self.han += 1
            if not(self.wins_by_ron) : self.han += 1
            if self.wins_by_rinshan_kaihou : self.han += 1
            if self.wins_by_last_tile : self.han += 1
            if self.wins_by_chankan : self.han += 1
            if all_simples(hand) : self.han += 1
            if flush(hand) : self.han += 6
            if half_flush(hand) : self.han += 3
            if all_terminals_and_honors(hand) : self.han += 2
            if player.reds[0] or player.opened_reds[0] : self.han += 1
            if player.reds[1] or player.opened_reds[1] : self.han += 1
            if player.reds[2] or player.opened_reds[2] : self.han += 1
            for i in range(5) :
                if self.dora_has_opened[i] :
                    self.han += hand[self.doras[i]]
                    if player.has_declared_ready or player.has_declared_double_ready : self.han += hand[self.uras[i]]
            if self.han > 13 : self.han = 13
            self.fu = 25


    # 基本点の計算
    def calculate_basic_points(self, player:Player) -> int :
        self.han = 0
        if self.wins_by_tenhou : self.yakuman += 1
        if self.wins_by_chiihou : self.yakuman += 1
        shanten_nums = self.shanten_calculator.get_shanten_nums(player.hand, player.opened_sets_num)
        if shanten_nums[0] == -1 : self.count_han_of_normal_hand(player)
        elif shanten_nums[1] == -1 : self.count_han_of_seven_pairs_hand(player)
        elif shanten_nums[2] == -1 : self.yakuman += 1

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
    def analyze_best_composition(self, player:Player) -> None :
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
                self.temp[self.i_temp] = BlockType.PAIR
                self.temp[self.i_temp+1] = i
                self.i_temp += 2
                self.pick_out_mentsu(player.has_stealed, hand);
                self.i_temp -= 2
                self.temp[self.i_temp] = 0
                self.temp[self.i_temp+1] = 0
                hand[i] += 2


    # 面子を抜き出す
    ## 和了が確定してからしか呼ばれないので高速化のためにPlayer._pick_out_mentsu()でやらなくていい部分を省いている．別物.
    def pick_out_mentsu(self, has_stealed:bool, hand:List[int]) -> None:
        for i in range(1,38) :
            if self.temp[9] != 0 :
                self.count_han(has_stealed)
                return
            if hand[i] == 0 : continue
            if hand[i] >= 3 :
                hand[i] -= 3
                if self.winning_tile == i and self.wins_by_ron and hand[i] == 0 : self.temp[self.i_temp] = BlockType.CLOSED_TRIPLET
                else : self.temp[self.i_temp] = BlockType.CLOSED_TRIPLET
                self.temp[self.i_temp + 1] = i
                self.i_temp += 2
                self.pick_out_mentsu(has_stealed, hand)
                self.i_temp -= 2
                self.temp[self.i_temp] = 0
                self.temp[self.i_temp + 1] = 0
                hand[i] += 3
            if i <= 27 and hand[i] > 0 and hand[i+1] > 0 and hand[i+2] > 0 :
                hand[i] -= 1
                hand[i+1] -= 1
                hand[i+2] -= 1
                self.temp[self.i_temp] = BlockType.CLOSED_RUN
                self.temp[self.i_temp+1] = i
                self.i_temp += 2
                self.pick_out_mentsu(has_stealed, hand)
                self.i_temp -= 2
                self.temp[self.i_temp] = 0
                self.temp[self.i_temp+1] = 0
                hand[i] += 1
                hand[i+1] += 1
                hand[i+2] += 1


    # 翻数を数える
    def count_han(self, has_stealed:bool) -> None :
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
            self.fu = self.calculate_fu(has_stealed)
        elif han_temp == self.han :
            fu_temp = self.calculate_fu(has_stealed)
            if fu_temp > self.fu : self.fu = fu_temp


    # 符計算
    def calculate_fu(self, has_stealed:bool) -> int :
        fu = 0
        if no_points_hand(self.temp, self.winning_tile, self.prevailing_wind, self.players_wind) :
            if self.wins_by_ron : return 30
            else : return 20
        fu = 20
        if not(has_stealed) and self.wins_by_ron : fu += 10
        elif not(self.wins_by_ron) : fu += 2
        for i in range(0, 10, 2) :
            if self.temp[i] == BlockType.CLOSED_RUN :
                if (self.temp[i+1] == self.winning_tile - 2 and self.temp[i+1] % 10 == 1) or \
                   (self.temp[i+1] == self.winning_tile and self.temp[i+1] % 10 == 7) or \
                   (self.temp[i+1] == self.winning_tile - 1) :
                    fu += 2
                    break
            elif self.temp[i] == BlockType.PAIR :
                if self.temp[i+1] == self.winning_tile :
                    fu += 2
                    break
        for i in range(0, 10, 2) :
            if self.temp[i] == BlockType.OPENED_TRIPLET :
                if self.temp[i+1] % 10 in [1,9] or self.temp[i+1] > 30 : fu += 4
                else : fu += 2
            elif self.temp[i] == BlockType.PAIR :
                if self.temp[i+1] >= 35 or self.temp[i+1] == self.prevailing_wind : fu += 2
                if self.temp[i+1] == self.players_wind : fu += 2
            elif self.temp[i] in BlockType.RUNS : continue
            elif self.temp[i] == BlockType.CLOSED_TRIPLET :
                if self.temp[i+1] % 10 in [1,9] or self.temp[i+1] > 30 : fu += 8
                else : fu += 4
            elif self.temp[i] == BlockType.OPENED_KAN :
                if self.temp[i+1] % 10 in [1,9] or self.temp[i+1] > 30 : fu += 16
                else : fu += 8
            elif self.temp[i] == BlockType.CLOSED_KAN :
                if self.temp[i+1] % 10 in [1,9] or self.temp[i+1] > 30 : fu += 32
                else : fu += 16
        if fu == 20 : fu = 30
        elif fu % 10 > 0 : fu = (fu + 10) - (fu % 10)
        return fu


    # ドローフェーズの処理
    def proc_draw_phase(self, player:Player) -> None :
        # ポン，チーした場合はスキップ
        if self.steal_flag : return

        # 槓した場合は嶺上牌から，そうでない場合は山からツモる
        if self.rinshan_draw_flag : tile = self.supply_next_rinshan_tile()
        else : tile = self.supply_next_tile()
        player.get_tile(tile)
        self.logger.register_got_tile(self.i_player, tile)

        # 和了の判定と和了時の事前変数操作
        self.win_flag = player.decide_win(self)
        if self.win_flag :
            player.wins = True
            self.set_winning_tile(player.last_got_tile)
            if self.rinshan_draw_flag : self.wins_by_rinshan_kaihou = True
            if self.wins_by_rinshan_kaihou is False : self.check_player_wins_by_last_tile() # 嶺上と河底は重複しない

        # 嶺上flagを元に戻す
        self.rinshan_draw_flag = False


    # 立直の処理
    def proc_ready(self, player:Player) -> None :
        self.ready_flag = True
        self.deposits_num += 1
        player.declare_ready(self.is_first_turn)


    # 暗槓が行われた時の処理
    def proc_ankan(self, tile:int) -> None :
        # 直前の行動が加槓だった場合このタイミングでドラが開く
        if self.dora_opens_flag :
            self.open_new_dora()
            self.dora_opens_flag = False

        if tile in TileType.REDS : tile += 5
        self.appearing_tiles[tile] += 4
        self.is_first_turn = False
        self.open_new_dora()
        self.rinshan_draw_flag = True
        for i in range(4) : self.players[i].has_right_to_one_shot = False
        self.players[self.i_player].proc_ankan(tile)
        self.logger.register_ankan(self.i_player, tile)


    # 加槓が行われた時の処理
    def proc_kakan(self, tile:int) -> None :
        if tile in TileType.REDS : tile += 5
        self.appearing_tiles[tile] += 1
        self.rinshan_draw_flag = True
        self.dora_opens_flag = True
        for i in range(4) : self.players[i].has_right_to_one_shot = False
        pos, red = self.players[self.i_player].proc_kakan(tile)
        self.logger.register_kakan(self.i_player, tile, pos, red)


    # アクションフェーズの処理
    def proc_action_phase(self) -> bool :
        # プレイヤの行動決定，tile:赤は(0,10,20)表示
        tile, exchanged, ready, ankan, kakan, kyushu = self.players[self.i_player].decide_action(self, self.players)

        if ready : self.proc_ready(self.players[self.i_player])
        elif ankan : self.proc_ankan(tile)
        elif kakan :
            # 直前の行動が加槓だった場合このタイミングでドラが開く
            if self.dora_opens_flag : self.open_new_dora()
            # 槍槓用ロンフェーズ
            self.proc_ron_phase(tile, True)
            if self.win_flag : return
            self.proc_kakan(tile)
        elif kyushu : self.is_abortive_draw = True

        return ready


    # 打牌フェーズ
    def proc_discard_phase(self, player:Player, ready:bool) -> None :
        # プレイヤが捨てる牌を決定，discarded_tile:赤は(0,10,20)表示
        discarded_tile = player.discard_tile()
        self.logger.register_discarded_tile(self.i_player, discarded_tile, ready)

        # 捨てられた牌を見えている牌に記録
        self.add_to_appearing_tiles(discarded_tile)

        # 鳴いた後に切った場合, 手出し牌に牌を記録
        if self.steal_flag : player.add_to_discard_tiles_after_stealing(discarded_tile)
        self.steal_flag = False
        if player.is_nagashi_mangan : self.players[self.i_player].check_player_is_nagashi_mangan()

        return discarded_tile


    # ロンフェーズ
    def proc_ron_phase(self, discarded_tile:int) -> None :
        winners_num = 0
        for i in range(1,4) :
            i_winner = (self.i_player + i) % 4
            if self.players[i_winner].decide_win(self, discarded_tile) :
                # リーチ宣言時のロンはリーチ不成立
                if self.ready_flag :
                    self.ready_flag = False
                    # リー棒返却
                    self.deposits_num -= 1
                    self.players[self.i_player].score_points(1000)

                # 和了人数をincrement
                winners_num += 1

                # 切られた牌を手牌に加える
                self.players[i_winner].get_tile(discarded_tile)

                # 和了牌を記録．平和判定とかに使う．
                self.set_winning_tile(discarded_tile)

                # 偶然役の記録
                if self.dora_opens_flag : self.wins_by_chankan = True # 槍槓があるかどうかを記録
                self.check_player_wins_by_last_tile() # 河底のチェック

                # ロン和了フラグを立てる
                self.win_flag = True
                self.wins_by_ron = True
                self.players[i_winner].wins = True

        # 三家和判定
        if winners_num == 3 :
            self.is_abortive_draw = True
            self.win_flag = False


    # 途中流局（四風連打，四家立直，四槓散了）の判定
    def check_game_is_abortive_draw(self, discarded_tile:int) -> None :
        #  四風連打の判定
        if self.is_first_turn and (4 + self.i_player - self.rotations_num) % 4 == 3 :
            if (discarded_tile in TileType.WINDS) and \
               (self.players[0].discarded_tiles[0] == self.players[1].discarded_tiles[0] == self.players[2].discarded_tiles[0] == self.players[3].discarded_tiles[0]) :
                self.is_abortive_draw = True

        #  四家立直の判定
        if (self.players[0].has_declared_ready or self.players[0].has_declared_double_ready) and \
           (self.players[1].has_declared_ready or self.players[1].has_declared_double_ready) and \
           (self.players[2].has_declared_ready or self.players[2].has_declared_double_ready) and \
           (self.players[3].has_declared_ready or self.players[3].has_declared_double_ready) :
            self.is_abortive_draw = True

        # 四槓散了判定．四槓散了は暗槓，加槓，大明槓どの場合でも牌がきられて通ったタイミングで判定される
        kans_num = 0
        for i in range(4) :
            if self.players[i].kans_num == 4 : return False # 一人で4回槓しているのは流局にならない
            kans_num += self.players[i].kans_num
        if kans_num == 4 :
            self.is_abortive_draw = True


    # 副露フェーズ
    def proc_steal_phase(self, discarded_tile:int) -> None :
        # ポン，カン判定と処理
        for i in range(1,4) :
            i_ap = (self.i_player + i) % 4 #i_ap : index of action player
            pon, kan = False, False
            pon, kan = self.players[i_ap].decide_pon_or_kan(self, self.players, discarded_tile)
            if (pon and kan) is False : continue
            else :
                self.players[self.i_player].is_nagashi_mangan = False
                for j in range(4) : self.players[j].has_right_to_one_shot = False
                if pon : self.proc_pon(i_ap, discarded_tile)
                elif kan : self.proc_daiminkan(i_ap, discarded_tile)
                break

        # チー判定と処理
        if (pon and kan) is False :
            i_ap = (self.i_player + 1) % 4 #i_ap : index of action player
            chii, tile1, tile2 = self.players[i_ap].decide_chii(self, self.players, discarded_tile) # tile1, tile2が赤の時は赤番号(0,10,20)で返す
            if chii :
                self.players[self.i_player].is_nagashi_mangan = False
                self.proc_chii(i_ap, discarded_tile, tile1, tile2)


    # 局の処理
    def play_subgame(self) -> None :
        # 局を初期化
        self.init_subgame()

        # 配牌を配る
        for i in range(4) :
            for j in range(13) :
                tile = self.supply_next_tile()
                self.players[i].get_tile(tile)
                self.logger.register_got_tile(i, tile, True)


        # ツモループ {
        while True :
            # 同順フリテン解消
            self.players[self.i_player].reset_same_turn_furiten()

            # ツモフェーズ
            self.proc_draw_phase(self.players[self.i_player])
            # ツモ和了ならループから抜ける
            if self.win_flag : break
            # 一発の権利がなくなる
            self.players[self.i_player].has_right_to_one_shot = False

            # アクションフェーズ
            ready = self.proc_action_phase()

            # 槍槓ロンならループから抜ける
            if self.win_flag : break
            # 暗槓，加槓の場合，次のツモにスキップ
            if self.rinshan_draw_flag : continue
            # 九種九牌用
            if self.is_abortive_draw : break

            # 打牌フェーズ
            discarded_tile = self.proc_discard_phase(self.players[self.i_player], ready)

            # 大明槓，加槓した場合牌を切った後にドラをめくる
            if self.dora_opens_flag :
                self.open_new_dora()
                self.dora_opens_flag = False

            # ロンフェーズ
            self.proc_ron_phase(discarded_tile)
            # ロン和了ならループから抜ける
            if self.win_flag : break

            # 途中流局の判定
            self.check_game_is_abortive_draw(discarded_tile)
            if self.is_abortive_draw : break

            # 切った牌を他家のフリテン牌にセット
            for i in range(1,4) :
                op = (self.i_player + i) % 4
                if self.players[op].has_declared_ready or self.players[op].has_declared_double_ready : self.players[op].add_furiten_tile(discarded_tile)
                else : self.players[op].add_same_turn_furiten_tile(discarded_tile)

            # 副露フェーズ
            self.proc_steal_phase(discarded_tile)

            # プレイヤインデックスを加算
            self.increment_i_player()

            # 1巡目かどうかの状態を更新
            if self.is_first_turn and self.i_player == 4 : self.is_first_turn = False

            # 通常流局判定
            if 136 - (self.i_wall + self.i_rinshan) == 14 : break

        # } ツモループ

        # プレイログをファイルとして保存
        self.logger.save(self)

        # 和了の処理
        if self.win_flag : self.proc_win()
        else :
            for i in range(4) : self.players[i].check_hand_is_ready()
            if self.is_abortive_draw : self.counters_num += 1
            # 流し満貫判定と処理
            elif ( self.players[0].is_nagashi_mangan or \
                   self.players[1].is_nagashi_mangan or \
                   self.players[2].is_nagashi_mangan or \
                   self.players[3].is_nagashi_mangan ) : self.proc_nagashi_mangan()
            # 和了，途中流局，流し満貫のどれでもなければ普通の流局処理
            else : self.proc_drawn_game()


    # 半荘の処理
    def play_game(self) -> None :
        count = 0
        while True :
            # 局
            self.play_subgame()
            # 半荘終了判定
            if self.is_over : break

        # 向聴テーブルをdump
        self.shanten_calculator.dump_table()


