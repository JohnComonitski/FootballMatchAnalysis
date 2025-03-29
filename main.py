from analysis.event import *
from analysis.player import *
from events.match import Match

# Load Event Data
DATADIR = './data'
game_id = 2

match = Match(DATADIR, game_id)
goals = match.goals()
goal_frame = goals.iloc[1].name

#plot_goal(match, goal_frame)
#plot_pitch_control(match, goal_frame)
positions_at_kickoff(match)