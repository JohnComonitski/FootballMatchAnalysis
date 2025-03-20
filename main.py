from analysis.event import plot_goal, plot_pitch_control
from analysis.player import track_distance_covered 

# Load Event Data
DATADIR = './data'
game_id = 2

plot_goal(DATADIR, game_id, 823)
plot_pitch_control(DATADIR, game_id, 822)
track_distance_covered(DATADIR, game_id)