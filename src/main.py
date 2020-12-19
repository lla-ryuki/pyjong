# std

# 3rd

# ours
from cymod.game import Game
from player.action import Action


if __name__ == "__main__" :
    action = Action()
    # ゲーム処理
    game = Game(action=action)
    game.play_game()
