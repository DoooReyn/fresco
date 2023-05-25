import os
import shutil

CURRENT_DIR = os.path.dirname(__file__)

def wrap_path(path):
    return os.path.join(CURRENT_DIR, path)

def copy_games(*args, **kwargs):
    GAMES_SRC_DIR = wrap_path("static/games")
    GAMES_DST_DIR = wrap_path("site/games")
    shutil.copytree(GAMES_SRC_DIR, GAMES_DST_DIR)