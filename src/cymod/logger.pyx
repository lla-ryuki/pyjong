# sys
import os
import sys
import string
import random
import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), './'))

# 3rd

# ours
from mytypes import TileType, BlockType

# cython
from libcpp cimport bool




cdef class Logger :
    cdef public str dir_path
    cdef public str save_path
    cdef public bool is_logging
    cdef public list actions
    cdef public list starting_hands
    cdef public list tiles_player_got

    def __init__(self, bool is_logging) :
        now = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")
        id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.dir_path = f"../data/log/{now}_{id}"
        try : os.mkdir(self.dir_path)
        except : pass
        self.save_path = f"../data/log/{now}.log"
        self.is_logging = is_logging
        self.actions = [[] for i in range(4)]
        self.starting_hands = [[] for i in range(4)]
        self.tiles_player_got = [[] for i in range(4)]


    cpdef void register_ankan(self, int i_player, int tile) :
        cdef str s_tile, text

        s_tile = str(tile + 10)
        if tile in TileType.FIVES :
            s_rtile = str(51 + (tile // 10))
            text = f"{s_tile}{s_tile}{s_tile}a{s_rtile}"
        else :
            text = f"{s_tile}{s_tile}{s_tile}a{s_tile}"

        self.actions[i_player].append(f"\"{text}\"")


    cpdef void register_kakan(self, int i_player, int tile, int pos, bool red) :
        cdef str s_tile, s_rtile, text

        s_tile = str(tile + 10)
        if tile in TileType :
            s_rtile = str(51 + (tile // 10))
            if red :
                if pos == 1 : text = f"{s_tile}{s_tile}{s_rtile}k{s_tile}"
                elif pos == 2 : text = f"{s_tile}k{s_tile}{s_tile}{s_rtile}"
                else : text = f"k{s_tile}{s_tile}{s_tile}{s_rtile}"
            else :
                if pos == 1 : text = f"{s_tile}{s_tile}{s_tile}k{s_rtile}"
                elif pos == 2 : text = f"{s_tile}k{s_rtile}{s_tile}{s_tile}"
                else : text = f"k{s_rtile}{s_tile}{s_tile}{s_tile}"
        elif pos == 1 : text = f"{s_tile}{s_tile}k{s_tile}{s_tile}"
        elif pos == 2 : text = f"{s_tile}k{s_tile}{s_tile}{s_tile}"
        else : text = f"k{s_tile}{s_tile}{s_tile}{s_tile}"

        self.actions[i_player].append(f"\"{text}\"")


    cpdef void register_daiminkan(self, int i_player, int tile, int pos) :
        cdef str s_tile, s_rtile, text

        s_tile = str(tile + 10)
        if tile in TileType.REDS :
            s_tile = str(tile + 15)
            s_rtile = str(51 + (tile // 10))
            if pos == 1 : text = f"{s_tile}{s_tile}{s_tile}m{s_rtile}"
            elif pos == 2 : text = f"{s_tile}m{s_rtile}{s_tile}{s_tile}"
            else : text = f"m{s_rtile}{s_tile}{s_tile}{s_tile}"
        elif tile in TileType.FIVES :
            s_rtile = str(51 + (tile // 10))
            if pos == 1 : text = f"{s_tile}{s_tile}{s_rtile}k{s_tile}"
            elif pos == 2 : text = f"{s_tile}m{s_tile}{s_tile}{s_rtile}"
            else : text = f"m{s_tile}{s_tile}{s_tile}{s_rtile}"
        elif pos == 1 : text = f"{s_tile}{s_tile}{s_tile}m{s_tile}"
        elif pos == 2 : text = f"{s_tile}m{s_tile}{s_tile}{s_tile}"
        else : text = f"m{s_tile}{s_tile}{s_tile}{s_tile}"

        self.tiles_player_got[i_player].append(f"\"{text}\"")



    cpdef void register_pon(self, int i_player, int tile, int pos) :
        cdef str s_tile, s_rtile, text

        s_tile = str(tile + 10)
        if tile in TileType.REDS :
            s_tile = str(tile + 15)
            s_rtile = str(51 + (tile // 10))
            if pos == 1 : text = f"{s_tile}{s_tile}p{s_rtile}"
            elif pos == 2 : text = f"{s_tile}p{s_rtile}{s_tile}"
            else : text = f"p{s_rtile}{s_tile}{s_tile}"
        elif tile in TileType.FIVES :
            s_rtile = str(51 + (tile // 10))
            if pos == 1 : text = f"{s_tile}{s_rtile}p{s_tile}"
            elif pos == 2 : text = f"{s_tile}p{s_tile}{s_rtile}"
            else : text = f"p{s_tile}{s_rtile}{s_tile}"
        elif pos == 1 : text = f"{s_tile}{s_tile}p{s_tile}"
        elif pos == 2 : text = f"{s_tile}p{s_tile}{s_tile}"
        else : text = f"p{s_tile}{s_tile}{s_tile}"

        self.tiles_player_got[i_player].append(f"\"{text}\"")


    cpdef void register_chii(self, int i_player, int tile, int tile1, int tile2) :
        cdef str s_tile, s_tile1, s_tile2
        s_tile, s_tile1, s_tile2 = str(tile + 10), str(tile1 + 10), str(tile2 + 10)
        if tile in TileType.REDS : s_tile = str(51 + (tile // 10))
        elif tile1 in TileType.REDS : s_tile1 = str(51 + (tile1 // 10))
        elif tile2 in TileType.REDS : s_tile2 = str(51 + (tile2 // 10))
        self.tiles_player_got[i_player].append(f"\"c{s_tile}{s_tile1}{s_tile2}\"")


    cpdef void register_got_tile(self, int i_player, int tile, bool is_starting_hand=False) :
        if tile in TileType.REDS : s_tile = str(51 + (tile // 10))
        else : s_tile = str(10 + tile)
        if is_starting_hand : self.starting_hands[i_player] .append(s_tile)
        else : self.tiles_player_got[i_player].append(s_tile)


    cpdef void register_discarded_tile(self, int i_player, int discarded_tile, bool ready) :
        cdef str s_discarded_tile
        if discarded_tile in TileType.REDS : s_discarded_tile = str(51 + (discarded_tile // 10))
        else : s_discarded_tile = str(10 + discarded_tile)
        if ready : self.actions[i_player].append(f"\"r{s_discarded_tile}\"")
        else : self.actions[i_player].append(s_discarded_tile)


    cpdef void save(self, game) :
        cdef int i
        cdef str text, caption
        cdef list temp, scores, dora_indicators, ura_indicators

        text = "{\"title\":[\"\",\"\"],\"name\":[\"\",\"\",\"\",\"\"],\"rule\":{\"aka\":1},\"log\":[["
        temp = []
        temp.append(game.rounds_num * 4 + game.rotations_num)
        temp.append(game.counters_num)
        temp.append(game.deposits_num)
        text += str(temp) + ","
        scores = []
        for i in range(4) : scores += [game.players[i].score]
        text += str(scores) + ","
        dora_indicators = []
        ura_indicators = []
        for i in range(5) :
            if game.dora_indicators[i] in TileType.REDS : dora_indicators += [51 + (game.dora_indicators[i] // 10)]
            else : dora_indicators += [game.dora_indicators[i] + 10]
            if game.ura_indicators[i] in TileType.REDS : ura_indicators += [51 + (game.ura_indicators[i] // 10)]
            else : ura_indicators += [game.ura_indicators[i] + 10]
        text += str(dora_indicators) + ","
        text += str(ura_indicators) + ","

        for i in range (4) :
            text += str(self.starting_hands[i]).replace("\'","")   + ","
            text += str(self.tiles_player_got[i]).replace("\'","") + ","
            text += str(self.actions[i]).replace("\'","")          + ","

        text += "[\"不明\"]]]}\n"

        if   game.rounds_num == 0 : caption = f"東{game.rounds_num+1}局{game.counters_num:02}本場"
        elif game.rounds_num == 1 : caption = f"南{game.rounds_num+1}局{game.counters_num:02}本場"
        elif game.rounds_num == 2 : caption = f"西{game.rounds_num+1}局{game.counters_num:02}本場"
        f = open(f"{self.dir_path}/{game.rounds_num+1}-{game.rotations_num+1}-{game.counters_num:02}_{caption}.log", mode="w")
        f.write(text)
        f.flush()
        f.close()

        self.actions = [[] for i in range(4)]
        self.starting_hands = [[] for i in range(4)]
        self.tiles_player_got = [[] for i in range(4)]
