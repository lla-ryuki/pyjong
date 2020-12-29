# built-in
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/cymod'))

# 3rd

# ours
from Test import TestGame
from action import Action

if __name__ == "__main__" :
    action = Action()
    game = TestGame(action)
    game.test_games()

