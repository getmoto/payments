import sys
from os.path import dirname as d
from os.path import abspath

root_dir = d(d(abspath(__file__))) + "/" + "backend"
sys.path.append(root_dir)
