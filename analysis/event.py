import metrica.Metrica_IO as mio
import metrica.Metrica_Viz as mviz
import metrica.Metrica_Velocities as mvel
import metrica.Metrica_PitchControl as mpc
import numpy as np

def plot_goal(DATADIR, game_id, frame):
    events = mio.read_event_data(DATADIR,game_id)

    # Data Prep & Processing 
    tracking_home = mio.tracking_data(DATADIR,game_id,'Home')
    tracking_away = mio.tracking_data(DATADIR,game_id,'Away')
    tracking_home = mio.to_metric_coordinates(tracking_home)
    tracking_away = mio.to_metric_coordinates(tracking_away)
    events = mio.to_metric_coordinates(events)
    tracking_home,tracking_away,events = mio.to_single_playing_direction(tracking_home,tracking_away,events)

    # Calculate Player Celocities
    tracking_home = mvel.calc_player_velocities(tracking_home,smoothing=True)
    tracking_away = mvel.calc_player_velocities(tracking_away,smoothing=True)

    # Plot Movement Leading Up To Goal
    fig,ax = mviz.plot_events( events.loc[frame-1: frame], color='k', indicators = ['Marker','Arrow'], annotate=True, )
    goal_frame = events.loc[frame]['Start Frame']
    fig,ax = mviz.plot_frame( tracking_home.loc[goal_frame], tracking_away.loc[goal_frame], figax = (fig,ax), include_player_velocities=True )
    fig.savefig("goal.png", format="png", bbox_inches="tight")

def plot_pitch_control(DATADIR, game_id, frame):
    events = mio.read_event_data(DATADIR,game_id)

    # Data Prep & Processing 
    tracking_home = mio.tracking_data(DATADIR,game_id,'Home')
    tracking_away = mio.tracking_data(DATADIR,game_id,'Away')
    tracking_home = mio.to_metric_coordinates(tracking_home)
    tracking_away = mio.to_metric_coordinates(tracking_away)
    events = mio.to_metric_coordinates(events)
    tracking_home,tracking_away,events = mio.to_single_playing_direction(tracking_home,tracking_away,events)

    # Calculate Player Velocities
    tracking_home = mvel.calc_player_velocities(tracking_home,smoothing=True)
    tracking_away = mvel.calc_player_velocities(tracking_away,smoothing=True)

    # Get All Shots And Goals In The Match
    shots = events[events['Type']=='SHOT']
    goals = shots[shots['Subtype'].str.contains('-GOAL')].copy()

    # GetPpitch Control Model Parameters
    params = mpc.default_model_params()

    # Find Goalkeepers For Offside Calculation
    GK_numbers = [mio.find_goalkeeper(tracking_home),mio.find_goalkeeper(tracking_away)]

    PPCF,xgrid,ygrid = mpc.generate_pitch_control_for_event(frame, events, tracking_home, tracking_away, params, GK_numbers, field_dimen = (106.,68.,), n_grid_cells_x = 50)
    fig, ax = mviz.plot_pitchcontrol_for_event(frame, events,  tracking_home, tracking_away, PPCF, annotate=True)
    fig.savefig("pitch_control.png", format="png", bbox_inches="tight")