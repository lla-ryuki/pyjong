# sys
from typing import List

# ours
from mytypes import TileType


class Action :
    def __init__(self) :
        self.reset_N()


    # 切る牌を決める
    def decide_which_tile_to_discard(self, game, players, player_num) -> (int, bool) :
        # エラーチェック
        if game.tag_name[0] not in {"D", "E", "F", "G"} : game.error("Wrong tag (in Player.action.decide_which_tile_to_discard()")
        if   game.tag_name[0] == "D" : i_player = 0
        elif game.tag_name[0] == "E" : i_player = 1
        elif game.tag_name[0] == "F" : i_player = 2
        elif game.tag_name[0] == "G" : i_player = 3
        if i_player != player_num : game.error("Player index don't match (in decide_which_tile_to_discard())")

        tile = int(game.tag_name[1:])
        discarded_tile = game.convert_tile(tile)
        exchanged = False
        if tile != game.org_got_tile : exchanged = True

        game.read_next_tag()
        return discarded_tile, exchanged


    # リーチするかどうか決める
    def decide_to_declare_ready(self, game, players, player_num) -> bool :
        if game.tag_name != "REACH" : return False

        # エラーチェック
        if player_num != int(game.attr["who"]) : game.error("Player index don't match (in decide_to_declare_ready())")

        game.read_next_tag()
        return True



