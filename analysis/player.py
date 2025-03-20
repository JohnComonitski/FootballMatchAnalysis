import metrica.Metrica_IO as mio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def track_distance_covered(DATADIR, game_id):
    events = mio.read_event_data(DATADIR,game_id)

    # Data Prep & Processing 
    tracking_home = mio.tracking_data(DATADIR,game_id, 'Home')
    tracking_away = mio.tracking_data(DATADIR,game_id, 'Away')
    tracking_home = mio.to_metric_coordinates(tracking_home)
    tracking_away = mio.to_metric_coordinates(tracking_away)
    events = mio.to_metric_coordinates(events)
    tracking_home,tracking_away,events = mio.to_single_playing_direction(tracking_home, tracking_away, events)

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