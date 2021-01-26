# built-in
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/cymod'))

# 3rd

# ours
from test_game import TestGame
from Player.action import Action

if __name__ == "__main__" :
    action = Action()
    game = TestGame(action)
    game.test()

