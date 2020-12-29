# built-in
import random
import xml.etree.ElementTree as et

# 3rd

# ours
from game import Game
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
    cdef public tag_name
    cdef public attr
    cdef public bool error
    cdef public int i_log
    cdef public int org_got_tile

    def __init__(self, action) :
        super(TestGame, self).__init__(action)
        self.error = False

    # 半荘開始時の初期化
    @override
    cpdef void init_game(self, xml) :
        self.xml = xml
        for i in range(4) : self.players[i].init_game()
        self.logger.init_game()
        self.rounds_num = 0                            # 場 0:東場，1:南場，2:西場
        self.rotations_num = 0                         # 局 0:1局目 ... 3:4局目
        self.counters_num = 0                          # 積み棒の数
        self.deposits_num = 0                          # 供託の数
        self.is_over = False                           # Trueになると半荘終了


    # 局開始時の初期化
    @override
    cdef bool init_subgame(self) :
        cdef int i

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
        self.remain_tiles_num = 136                    # 山の残り枚数

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
        cdef bool error
        self.read_next_tag()

        # 局の情報に食い違いがあったらエラーとして報告
        seed = self.attr["seed"].split(",")
        if (self.rounds_num != int(seed[0]) // 4) or \
           (self.rotations_num != int(seed[0]) % 4) or \
           (self.counters_num != int(seed[1])) or \
           (self.deposits_num != int(seed[2])) and not(self.error) : self.error("subgame info")

        # プレイヤの点数に食い違いがあったらエラーとして報告
        ten = self.attr["ten"].split(",")
        error = False
        for i in range(4) :
            if (self.players[i].score != int(ten[i]) * 100) and (not(self.error)) : error("score")

        # 配牌を配る
        for i in range(4) :
            starting_hand = [self.convert_tile(int(tile)) for tile in self.attr[f"hai{i}"].split(",")]
            for tile in starting_hand : self.players[i].get_tile(tile)

        # 初期ドラをセット
        indicator = self.convert_tile(int(seed[5]))
        self.dora_indicators[0] = indicator
        self.open_new_dora()


    # 次のツモ牌を返す
    @override
    cdef int supply_next_tile(self) :
        cdef int tile
        if self.tag_name[0] not in {"T", "U", "V", "W"} : self.error("Wrong tag (in game.supply_next_rinshan_tile()")
        tile = int(self.tag_name[1:])
        self.i_wall += 1
        self.remain_tiles_num -= 1
        self.read_next_tag()
        return tile


    # 次の嶺上牌を返す
    @override
    cdef int supply_next_rinshan_tile(self) :
        cdef int tile
        if self.tag_name[0] not in {"T", "U", "V", "W"} : self.error("Wrong tag (in game.supply_next_rinshan_tile()")
        tile = int(self.tag_name[1:])
        self.i_rinshan += 1
        self.remain_tiles_num -= 1
        self.read_next_tag()
        return tile


    # UN，REACH(step2)タグ以外の次のタグを読んで，tag_name，attrをメンバ変数にセット
    cpdef void read_next_tag(self) :
        self.i_log += 1
        while True :
            tag_name = self.xml[self.i_log].item.tag
            attr = self.xml[self.i_log].item.attrib
            if tag_name != "UN" and not(tag_name == "REACH" and attr["step"] == 2) :
                self.tag_name = tag_name
                self.attr = attr
                break
            self.i_log += 1


    # xml_logの牌番号をこのプログラムの牌番号に変換
    cdef int convert_tile(self, int org_tile) :
        if org_tile in {16, 52, 88} : tile = (org_tile // 40) * 10
        else :
            tile = org_tile // 4
            if tile >= 27 : tile += 4
            elif tile >= 18 : tile += 3
            elif tile >= 9 : tile += 2
            else : tile += 1

        return tile


    # ログと食い違いが起こった時の処理
    cpdef void error(self, info) :
        self.error = True
        print("==============================")
        print(info)
        print(f"file_name : {self.file_name} \n round:{self.rounds_num} \n rotation:{self.rotations_num} \n counter:{self.counters_num} \n ")


    # 半荘の処理
    cpdef void play_test_game(self) :
        cdef int i
        for i in range(games_num) :
            self.init_game()
            while True :
                # 局
                self.play_subgame()
                # 半荘終了判定
                if self.is_over : break


    # テスト用メソッド
    cpdef void test(self, action) :
        year = int(input("Input year : "))
        for month in range(1, 12) :
            path = f"../data/xml/{year}/{month:02}/"
            dir_components = os.listdir(path)
            files = [f for f in dir_components if os.path.isfile(os.path.join(path, f))]
            print(f"year:{year}, month:{month}")
            for file_name in files :
                # 空ファイルが紛れていることがあるのでそれをスキップ
                try : tree = et.parse(path + file_name)
                except : continue

                xml = tree.getroot()
                game.init_game(xml[3:])
                game.play_game()
