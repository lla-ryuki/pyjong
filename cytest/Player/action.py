# sys
from typing import List

# ours
from mytypes import TileType


class Action :
    def __init__(self) :
        self.reset_N()


    # 鳴きで使うメンバ変数をreset
    def reset_N(self) :
        self.tile = -1
        self.tile1 = -1
        self.tile2 = -1
        self.pos = -1
        self.contain_red = False


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


    # 鳴くかどうか決める
    def decide_to_steal(self, game, players, tile, pos, player_num) -> (int, int, int, int, int, int) :
        pass


    # 槓するかどうか決める
    def decide_to_kan(self, game, players, player_num:int, ankan_tiles:List[int], kakan_tiles:List[int]) -> int :
        if game.tag_name != "N" : return -1

        # タグのmcから槓する牌を判定
        mc = int(game.attr["m"])
        action_num = self.analyze_mc(mc)
        tile = self.tile

        # エラーチェック
        if player_num != int(game.attr["who"]) : game.error("Player index don't match (in decide_to_kan())")
        if action_num not in {6, 7} : game.error("Wrong tag (in Player.aciton.decide_to_kan())")

        self.reset_N()
        game.read_next_tag()
        return tile


    # 九種九牌を宣言するかどうか決める
    def decide_to_declare_nine_orphans(self, game, players, player_num:int, hand:List[int]) -> bool :
        if not(game.tag_name == "RYUUKYOKU" and game.attr["type"] == "yao9") : return False

        game.read_next_tag()
        return True


    # リーチするかどうか決める
    def decide_to_declare_ready(self, game, players, player_num) -> bool :
        if game.tag_name != "REACH" : return False

        # エラーチェック
        if player_num != int(game.attr["who"]) : game.error("Player index don't match (in decide_to_declare_ready())")

        game.read_next_tag()
        return True


    # 和了かどうかタグを見て判断
    def decide_win(self, game, players, player_num:int) -> bool :
        if game.tag_name != "AGARI" : return False

        game.read_next_tag()
        return True


    # Nタグについているmコードを解析してそれぞれの鳴きに対する処理をする
    def analyze_mc(self, player_num:int, mc:int) -> int :
        # チー
        if  (mc & 0x0004) :
            pt = (mc & 0xFC00) >> 10
            r  = pt % 3
            pn = pt // 3
            color = pn // 7
            n  = (color * 10) + (pn % 7) + 1
            run = [n, n+1, n+2]
            pp = [(mc & 0x0018) >> 3, (mc & 0x0060) >> 5, (mc & 0x0180) >> 7]
            for i in range(3) :
                if (run[i] % 10 == 5 and pp[i] == 0) : run[i] -= 5
            if   r == 0 : self.tile, self.tile1, self.tile2 = run[0], run[1], run[2]
            elif r == 1 : self.tile, self.tile1, self.tile2 = run[1], run[0], run[2]
            elif r == 2 : self.tile, self.tile1, self.tile2 = run[2], run[0], run[1]
            return 3 + r

        # ポン
        elif(mc & 0x0008) :
            self.pos = mc & 0x0003
            pt = (mc & 0xFE00) >> 9
            r  = pt % 3
            pn =  pt // 3
            color = pn // 9
            self.tile = (color * 10) + (pn % 9) + 1
            self.contain_red = False
            if(color != 3 and self.tile % 10 == 5) :
                if ((mc & 0x0060) == 0) : pass
                elif (r == 0)           : self.tile -= 5
                else                    : self.contain_red = True
            return 1

        # 加槓
        elif(mc & 0x0010) :
            self.pos = mc & 0x0003
            pt = (mc & 0xFE00) >> 9
            r  = pt % 3
            pn =  pt // 3
            color = pn // 9
            self.tile = (color * 10) + (pn % 9) + 1
            return 6

        # 大明槓, 暗槓
        else :
            self.pos = mc & 0x0003
            pt = (mc & 0xFF00) >> 8
            r  = pt % 4
            pn =  pt // 4
            color = pn // 9  # 0:萬子,...
            self.tile = (color * 10) + (pn % 9) + 1
            action = 2
            if(color != 3 and self.tile % 10 == 5) :
                if (self.pos == 0) : action = 7
                elif (r == 0) : self.tile -= 5
            return action


