# std
import xml.etree.ElementTree as et

# 3rd

# ours
from game_feed import Game


if __name__ == "__main__" :
    file_name = "2019101200gm-00a9-0000-2d55440c.xml"
    tree = et.parse(f"../data/xml/2019/{file_name}")
    root = tree.getroot()


    # ゲーム処理
    game = Game(root)
    game.play_game()
