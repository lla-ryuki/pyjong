# built-in
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), './cymod'))

# 3rd
from termcolor import colored

# ours
from game import Game
from Player.action import Action


if __name__ == "__main__" :
    games_num = int(input(colored("Input games num: ","yellow", attrs=["bold"])))

    action = Action()
    game = Game(action=action, logging=True, testing=False)
    game.play_games(games_num)
