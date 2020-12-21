# built-in
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), './cymod'))

# 3rd

# ours
from game import Game
from Player.action import Action


if __name__ == "__main__" :
    action = Action()
    # ゲーム処理
    game = Game(action=action)
    game.play_game()
