import sys
from os.path import abspath, join, dirname, pardir
root_path = abspath(join(dirname(__file__), pardir))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
src_path = join(root_path, "generic_parser")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import generic_parser