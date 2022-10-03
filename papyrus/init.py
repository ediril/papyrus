from distutils.dir_util import copy_tree

from .config import *

def init(args, conf):

    print("Initializing new static site...")
    print("Target directory: {}".format(pathlib.Path('.').resolve()))

    if any(pathlib.Path('.').iterdir()):
        print("WARNING: Target directory is not empty!")

    bootstrap_path = pathlib.Path(__file__).parent / BOOTSTRAP_PATH
    copy_tree(bootstrap_path.resolve(), str(pathlib.Path('.').resolve()))

    templates_path = pathlib.Path(__file__).parent / TEMPLATES_PATH
    destination_path = pathlib.Path('..') / TEMPLATES_PATH
    copy_tree(templates_path.resolve(), str(destination_path.resolve()))
