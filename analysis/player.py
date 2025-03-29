import metrica.Metrica_Viz as mviz
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def track_distance_covered(match, name=None):
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

    tracking_away = match.tracking_away

    # Create A Physical Summary Dataframe For Away Players
    away_players = np.unique( [ c.split('_')[1] for c in tracking_away.columns if c[:4] == 'Away' ] )
    away_summary = pd.DataFrame(index=away_players)

    # Calc Total Distance Covered For Each Player
    distance = []
    for player in away_summary.index:
        column = 'Away_' + player + '_speed'
        player_distance = tracking_away[column].sum()/25./1000
        distance.append(player_distance)
    away_summary['Distance [km]'] = distance
    
    summary = pd.concat([home_summary, away_summary], axis=1)

    # Bar Chart of Distance Covered For Each Player
    plt.subplots()
    ax = summary['Distance [km]'].plot.bar(rot=0)
    ax.set_xlabel('Player')
    ax.set_ylabel('Distance covered [km]')

    if not name:
        name = "distance.png"
    plt.savefig(name, format="png", bbox_inches="tight")

def positions_at_kickoff(match, name=None):
    frame = 1
    tracking_home = match.tracking_home
    tracking_away = match.tracking_away

    fig,ax = mviz.plot_frame( tracking_home.loc[frame], tracking_away.loc[frame])
 
    if not name:
        name = "kickoff.png"
    fig.savefig(name, format="png", bbox_inches="tight")

