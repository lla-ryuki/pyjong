# built-in
import os
import string
import random
import datetime

# 3rd

# ours
from mytypes import TileType, BlockType


class Logger :
    def __init__(self, is_logging:bool) :
        self.is_logging = is_logging


    def init_game(self) :
        now = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")
        id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.dir_path = f"../data/log/{now}_{id}"
        try : os.mkdir(self.dir_path)
        except : pass
        self.save_path = f"../data/log/{now}.log"
        self.actions = [[] for i in range(4)]
        self.starting_hands = [[] for i in range(4)]
        self.tiles_player_got = [[] for i in range(4)]


    def register_ankan(self, i_player:int, tile:int) -> None :
        s_tile = str(tile + 10)
        if tile in TileType.FIVES :
            s_rtile = str(51 + (tile // 10))
            text = f"{s_tile}{s_tile}{s_tile}a{s_rtile}"
        else :
            text = f"{s_tile}{s_tile}{s_tile}a{s_tile}"

        self.actions[i_player].append(f"\"{text}\"")


    def register_kakan(self, i_player:int, tile:int, pos:int, red:bool) -> None :
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


    def register_daiminkan(self, i_player:int, tile:int, pos:int) -> None :
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


    def register_pon(self, i_player:int, tile:int, pos:int) :
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


    def register_chii(self, i_player:int, tile:int, tile1:int, tile2:int) -> None :
        s_tile, s_tile1, s_tile2 = str(tile + 10), str(tile1 + 10), str(tile2 + 10)
        if tile in TileType.REDS : s_tile = str(51 + (tile // 10))
        elif tile1 in TileType.REDS : s_tile1 = str(51 + (tile1 // 10))
        elif tile2 in TileType.REDS : s_tile2 = str(51 + (tile2 // 10))
        self.tiles_player_got[i_player].append(f"\"c{s_tile}{s_tile1}{s_tile2}\"")


    def register_got_tile(self, i_player:int, tile:int, is_starting_hand:bool=False) -> None :
        if tile in TileType.REDS : s_tile = str(51 + (tile // 10))
        else : s_tile = str(10 + tile)
        if is_starting_hand : self.starting_hands[i_player] .append(s_tile)
        else : self.tiles_player_got[i_player].append(s_tile)


    def register_discarded_tile(self, i_player:int, discarded_tile:int, ready:bool ) -> None:
        if discarded_tile in TileType.REDS : s_discarded_tile = str(51 + (discarded_tile // 10))
        else : s_discarded_tile = str(10 + discarded_tile)
        if ready : self.actions[i_player].append(f"\"r{s_discarded_tile}\"")
        else : self.actions[i_player].append(s_discarded_tile)


    def save(self, game) -> None :
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

