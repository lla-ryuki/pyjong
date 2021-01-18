# built-in
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/cymod'))

# 3rd
from termcolor import colored

# ours
from test_game import TestGame
from Player.action import Action

if __name__ == "__main__" :
    action = Action()
    game = TestGame(action)
    log_id = input(colored("Input log id : ", "yellow"))
    game.partial_test(log_id)
