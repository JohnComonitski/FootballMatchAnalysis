import metrica.Metrica_IO as mio
import metrica.Metrica_Viz as mviz
import metrica.Metrica_PitchControl as mpc
import numpy as np
from .plot import Plot
import matplotlib.pyplot as plt
import pandas as pd

def plot_event(frame, name=None, c='k', plot=None, annotate=True):
    figax = None
    if plot:
        figax = ( plot.fig, plot.ax )

    indicator = "Marker"
    if( frame["Type"] in [ "PASS", "SHOT" ] ):
        indicator = "Arrow"

    fig,ax = mviz.plot_event( frame, figax=figax, color=c, indicators = indicator, annotate=annotate )
    plot = Plot(fig, ax) 

    return plot

def plot_goal(match, frame, name=None, c='k', plot=None):
    figax = None
    if plot:
        figax = ( plot.fig, plot.ax )

    events = match.events
    tracking_home = match.tracking_home
    tracking_away = match.tracking_away

    # Plot Movement Leading Up To Goal
    fig,ax = mviz.plot_events( events.loc[frame-1: frame], figax=figax, color=c, indicators = ['Marker','Arrow'], annotate=True, )
    goal_frame = events.loc[frame]['Start Frame']
    fig,ax = mviz.plot_frame( tracking_home.loc[goal_frame], tracking_away.loc[goal_frame], figax = (fig,ax), include_player_velocities=True )
    plot = Plot(fig, ax) 

    return plot

def plot_pitch_control(match, frame, name=None, c='k', plot=None):
    figax = None
    if plot:
        figax = ( plot.fig, plot.ax )

    events = match.events
    tracking_home = match.tracking_home
    tracking_away = match.tracking_away

    # Get Pitch Control Model Parameters
    params = mpc.default_model_params()

    # Find Goalkeepers For Offside Calculation
    GK_numbers = [mio.find_goalkeeper(tracking_home),mio.find_goalkeeper(tracking_away)]

    PPCF,xgrid,ygrid = mpc.generate_pitch_control_for_event(frame, events, tracking_home, tracking_away, params, GK_numbers, field_dimen = (106.,68.,), n_grid_cells_x = 50)
    fig, ax = mviz.plot_pitchcontrol_for_event(frame, events,  tracking_home, tracking_away, PPCF, annotate=True, figax=figax)
    plot = Plot(fig, ax) 

    return plot

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

def positions_at_kickoff(match, name=None, plot=None):
    figax = None
    if plot:
        figax = ( plot.fig, plot.ax )

    frame = 1
    tracking_home = match.tracking_home
    tracking_away = match.tracking_away

    fig,ax = mviz.plot_frame( tracking_home.loc[frame], tracking_away.loc[frame], figax=figax)
    plot = Plot(fig, ax) 
    
    return plot

