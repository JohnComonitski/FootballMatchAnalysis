from analysis.events import *
from objects.match import Match
from analysis.xt import *
from analysis.xg import *
from analysis.utils import *
from analysis.zones import *
import time
import pprint

pp = pprint.PrettyPrinter(indent=4)
pp = pprint.PrettyPrinter(width=41, compact=True)

# Load Event Data
DATADIR = './data'
game_id = 1

plot = Plot()
match = Match(DATADIR, game_id)