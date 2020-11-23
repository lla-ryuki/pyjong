# std
import os
import xml.etree.ElementTree as et

# 3rd

# ours
from log_game import Game
from log_player import Player
from feed import Feed


if __name__ == "__main__" :
    path = f"../data/test/"

    dir_components = os.listdir(path)
    files = [f for f in dir_components if os.path.isfile(os.path.join(path, f))]

    feed = Feed()

    for file_name in files :
        tree = et.parse(path + file_name)
        root = tree.getroot()
        # game = Game(root, file_name, feed_mode=False, feed=None) # feedは作らない時
        game = Game(root, file_name, feed_mode=True, feed=feed) # feedを作りたい時
        game.read_log()
