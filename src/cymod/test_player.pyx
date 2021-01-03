from termcolor import colored
from player cimport Player

cdef class TestPlayer(Player) :
    def __init__(self, player_num) :
        super().__init__(player_num)

    # リーチ時のツモ切る牌と手出し状態を返す
    cpdef tuple discard_tile_when_player_has_declared_ready(self, game, players, int player_num) :
        if game.tag_name[0] not in {"D", "E", "F", "G"} : game.error("Wrong tag (in TestPlayer.discard_tile_when_player_has_declared_ready())")
        if   game.tag_name[0] == "D" : i_player = 0
        elif game.tag_name[0] == "E" : i_player = 1
        elif game.tag_name[0] == "F" : i_player = 2
        elif game.tag_name[0] == "G" : i_player = 3
        if i_player != player_num : game.error("Player index don't match (in TestPlayer.discard_tile_when_player_has_declared_ready())")

        tile = int(game.tag_name[1:])
        discarded_tile = game.convert_tile(tile)
        dis = colored("dis", "yellow")
        print(f"player{player_num} {dis} {discarded_tile}")
        exchanged = False
        if tile != game.org_got_tile : exchanged = True
        if discarded_tile != players[player_num].last_got_tile or exchanged : game.error("Discarded tile isn't match (in discard_tile_when_player_has_declared_ready())")

        game.read_next_tag()
        return discarded_tile, exchanged

