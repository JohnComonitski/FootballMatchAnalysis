import metrica.Metrica_IO as mio
import metrica.Metrica_Viz as mviz
import metrica.Metrica_PitchControl as mpc
import numpy as np

def plot_goal(match, frame):
    events = match.events
    tracking_home = match.tracking_home
    tracking_away = match.tracking_away

    # Plot Movement Leading Up To Goal
    fig,ax = mviz.plot_events( events.loc[frame-1: frame], color='k', indicators = ['Marker','Arrow'], annotate=True, )
    goal_frame = events.loc[frame]['Start Frame']
    fig,ax = mviz.plot_frame( tracking_home.loc[goal_frame], tracking_away.loc[goal_frame], figax = (fig,ax), include_player_velocities=True )
    fig.savefig("goal.png", format="png", bbox_inches="tight")

def plot_pitch_control(match, frame):
    events = match.events
    tracking_home = match.tracking_home
    tracking_away = match.tracking_away

    # Get Pitch Control Model Parameters
    params = mpc.default_model_params()

    # Find Goalkeepers For Offside Calculation
    GK_numbers = [mio.find_goalkeeper(tracking_home),mio.find_goalkeeper(tracking_away)]

    PPCF,xgrid,ygrid = mpc.generate_pitch_control_for_event(frame, events, tracking_home, tracking_away, params, GK_numbers, field_dimen = (106.,68.,), n_grid_cells_x = 50)
    fig, ax = mviz.plot_pitchcontrol_for_event(frame, events,  tracking_home, tracking_away, PPCF, annotate=True)
    fig.savefig("pitch_control.png", format="png", bbox_inches="tight")