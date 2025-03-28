import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def track_distance_covered_home(match, name=None):
    tracking_home = match.tracking_home

    # Create A Physical Summary Dataframe For Home Players
    home_players = np.unique( [ c.split('_')[1] for c in tracking_home.columns if c[:4] == 'Home' ] )
    home_summary = pd.DataFrame(index=home_players)

    # Calc Total Distance Covered For Each Player
    distance = []
    for player in home_summary.index:
        column = 'Home_' + player + '_speed'
        player_distance = tracking_home[column].sum()/25./1000
        distance.append(player_distance)
    home_summary['Distance [km]'] = distance

    # Bar Chart of Distance Covered For Each Player
    plt.subplots()
    ax = home_summary['Distance [km]'].plot.bar(rot=0)
    ax.set_xlabel('Player')
    ax.set_ylabel('Distance covered [km]')

    if not name:
        name = "distance.png"
    plt.savefig(name, format="png", bbox_inches="tight")

def positions_at_kickoff(match):
    pass

