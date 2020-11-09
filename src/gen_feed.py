# std
import xml.etree.ElementTree as et

# 3rd

# ours
from game_feed import Game

tree = et.parse('./log/log.xml')
root = tree.getroot()


if __name__ == "__main__" :
    # ゲーム処理
    game = Game()
    game.proc_game()
