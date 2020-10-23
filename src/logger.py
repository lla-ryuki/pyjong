from typing import List
import datetime

from game import Game
from player import Player
from tile_type import TileType


class Logger :

    def __init__(self, is_logging:bool) :
        now = datetime.datetime.now().isoformat()
        self.save_path = f"../data/log/{now}.log"
        self.is_logging = logging
        self.scores = [0] * 4
        self.actions = [[] for i in range(4)]
        self.starting_hands = [[] for i in range(4)]
        self.tiles_player_got = [[] for i in range(4)]


    def register_kan(self, i_player:int, tile:int) -> None :
        s_tile = str(tile + 10)
        self.actions[i_player].append(f"{s_tile}{s_tile}{s_tile}a{s_tile}")


    def register_kakan(self, i_player:int, tile:int) -> None :
        s_tile = str(tile + 10)
        self.actions[i_player].append(f"{s_tile}{s_tile}{s_tile}a{s_tile}")


    def register_got_tile(self, i:int, tile:int, is_starting_hand:bool = False) -> None :
        if tile in TileType.REDS : tile = 51 + (tile // 10)
        else : tile = 10 + tile
        if is_starting_hand : self.starting_hands[i] .append(tile)
        else : self.tiles_player_got[i].append(tile)


    def register_discarded_tile(self, i:int, discarded_tile: int, ready: bool) -> None :
        log_text = ""
        if ready : log_text = "r"
        if discarded_tile in TileType.REDS : discarded_tile_str = str(51 + (discarded_tile // 10))
        else : discarded_tile_str = str(10 + discarded_tile)
        self.actions[i].append(log_text + discarded_tile_str)


    def save(game: Game) -> None :
        text = "{\"title\":[\"\",\"\"],\"name\":[\"\",\"\",\"\",\"\"],\"rule\":{\"aka\":1},\"log\":[["
        temp = []
        temp.append(game.rounds_num * 4 + game.rotations_num)
        temp.append(game.counters_num)
        temp.append(game.deposits_num)
        text += str(temp) + ","
        scores = []
        for i in range(4) : scores += [scores[i]]
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
            text += str(self.starting_hands[i]) + ","
            temp = str(self.tiles_player_got[i])
            temp = temp.replace('\'','\"')
            text += temp + ","
            temp = str(self.actions[i])
            temp = temp.replace('\'','\"')
            text += temp + ","

        text += "[\"不明\"]]]}\n"

        f = open(self.save_path, mode="a")
        f.write(text)
        f.flush()
        f.close()

