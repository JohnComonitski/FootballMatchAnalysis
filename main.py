from analysis.event import *
from analysis.player import *
from events.match import Match

# Load Event Data
DATADIR = './data'
game_id = 2

match = Match(DATADIR, game_id)

plot_goal(match, 823)
plot_pitch_control(match, 822)
track_distance_covered_home(match)