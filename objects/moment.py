import FootballMatchAnalysis.metrica.Metrica_IO as mio
import FootballMatchAnalysis.metrica.Metrica_Viz as mviz
import FootballMatchAnalysis.metrica.Metrica_PitchControl as mpc
from FootballMatchAnalysis.objects.plot import Plot
from FootballMatchAnalysis.objects.player import Player
from FootballMatchAnalysis.objects.ball import Ball
from FootballMatchAnalysis.analysis.utils import *
from FootballMatchAnalysis.analysis.xg import *
from FootballMatchAnalysis.analysis.xt import *
import numpy as np

class Moment:
    def __init__(self, frame, event, home, away, time, game_state):
        self.frame = frame
        self.home = home
        self.away = away
        self.event = event
        self.PPCF = None
        self.time = time
        self. game_state = game_state
        self.ball = Ball(self.home["ball_x"], self.home["ball_y"], None, None, None)

    def plot_moment(self, c='k', plot=None, annotate=True, team_colors=('r','b'), field_dimen = (106.0,68.0), include_player_velocities=False, PlayerMarkerSize=10, PlayerAlpha=0.7 ):
        figax = None
        if plot:
            figax = ( plot.fig, plot.ax )

        fig,ax = mviz.plot_moment(frame=self.event, hometeam=self.home, awayteam=self.away, figax=figax, annotate=annotate, team_colors=team_colors, field_dimen = field_dimen, include_player_velocities=include_player_velocities, PlayerMarkerSize=PlayerMarkerSize, PlayerAlpha=PlayerAlpha  )
        plot = Plot(fig, ax) 

        return plot

    def home_team(self):
        return get_team(self.home)

    def away_team(self):
        return get_team(self.away)

    def possession(self, threshold=.5):
        players = self.home_team() + self.away_team()
        min_dist = 100
        dists = min_distances(self.ball, players)
        if(len(dists) > 0):
            min_dist = min(dists)

        for player in players:
            dist = distance((self.ball.x, self.ball.y), (player.x, player.y))
            if dist == min_dist and min_dist < threshold:
                return player
        return None
    
    def players_competeing_for_ball(self):
        players = self.home_team() + self.away_team()

        on_ball = []
        for player in players:
            player_x = player.x
            player_y = player.y
            dist = distance((self.ball.x, self.ball.y), (player_x, player_y))
            if str(dist) != "nan" and dist < 1:
                on_ball.append(player)

        return on_ball
    
    def distance_from_ball(self, player):
        return distance((self.ball.x, self.ball.y), (player.x, player.y))

    def generate_pitch_control(self):
        tracking_home = self.home.to_frame().T
        tracking_home.index.name = "Frame"
        tracking_home.reset_index(inplace=True)
        
        tracking_away = self.away.to_frame().T
        tracking_away.index.name = "Frame"
        tracking_away.reset_index(inplace=True)

        # Get Pitch Control Model Parameters
        params = mpc.default_model_params()

        GK_numbers = [mio.find_goalkeeper(tracking_home),mio.find_goalkeeper(tracking_away)]
        self.PPCF,xgrid,ygrid = mpc.generate_pitch_control_for_moment(self, tracking_home, tracking_away, params, GK_numbers, field_dimen = (106.,68.,), n_grid_cells_x = 107)

    def pass_probability(self, target):
        tracking_home = self.home.to_frame().T
        tracking_home.index.name = "Frame"
        tracking_home.reset_index(inplace=True)
        
        tracking_away = self.away.to_frame().T
        tracking_away.index.name = "Frame"
        tracking_away.reset_index(inplace=True)

        # Get Pitch Control Model Parameters
        params = mpc.default_model_params()

        GK_numbers = [mio.find_goalkeeper(tracking_home),mio.find_goalkeeper(tracking_away)]

        return mpc.calculate_pitch_control_at_target_for_moment(self, target, tracking_home, tracking_away, params, GK_numbers)

    def plot_pitch_control(self, plot):
        figax = None
        if plot:
            figax = ( plot.fig, plot.ax )

        if self.PPCF is None:
            self.generate_pitch_control()

        fig, ax = mviz.plot_pitchcontrol_for_moment( self.PPCF, field_dimen = (106.0,68), figax=figax)
        plot = Plot(fig, ax) 
        return plot
    
    def evaluate_passing_options(self, generate_video=False, metadata={}):
        on_ball = self.possession()
        team_with_ball = on_ball.team

        if team_with_ball == "Home":
            players = self.home_team()
        elif team_with_ball == "Away":
            players = self.away_team()

        best_xt = None
        best_pass = None
        pass_to = None
        best_frame = None

        i = 0
        if generate_video:
            i = metadata["i"]

        for player in players:
            if on_ball.name != player.name:
                pass_start = (on_ball.x, on_ball.y)
                if is_pass_possible(self, (player.x, player.y)):
                    for point in player.coords_in_radius():
                        if(str(pass_start[0]) != "nan" and str(point[0]) != "nan"):
                            if on_ball.in_peripheral_vision(player.x, player.y):
                                if in_front_of_player(pass_start, (player.x, player.y), point):
                                    p = self.pass_probability(point)

                                    new_plot = None
                                    if generate_video:
                                        new_plot = self.plot_moment(include_player_velocities=True)
                                        new_plot.draw_line(pass_start, point)
                                    
                                    xt = get_xt(point)
                                    if xt is not None:
                                        p_xt = xt * p
                                        save_pass = False
                                        if best_xt is None:
                                            save_pass = True
                                        elif(p_xt > best_xt):
                                            save_pass = True


                                        if save_pass:
                                            best_xt = p_xt
                                            best_pass = [ pass_start, point ]
                                            pass_to = player
                                            if generate_video:
                                                best_frame = new_plot

                                        if generate_video:
                                            metadata["current_xt"] = p_xt
                                            metadata["current_change_xt"] = p_xt - metadata["start_xt"]
                                            if p_xt > metadata["best_xt"]:
                                                metadata["best_xt"] = p_xt
                                                metadata["best_change_xt"] = p_xt - metadata["start_xt"]

                                            new_plot = metadata["annotate_plot"](new_plot, metadata["start_xt"], metadata["actual_xt"], metadata["best_xt"], metadata["current_xt"], metadata["best_change_xt"], metadata["current_change_xt"], metadata["frame"])
                                            new_plot.print(f"./frames/{i}.png")
                                            metadata["i"] = metadata["i"] + 1
                                            i = metadata["i"]
                                    if generate_video:
                                        new_plot.close()
        res = {
            "xt": best_xt,
            "pass": best_pass,
            "target": pass_to
        }

        if generate_video:
            res["frame"] = best_frame
            res["metadata"] = metadata

        return res

def min_distances(ball, players):
    dists = []
    for player in players:
        player_x = player.x
        player_y = player.y
        dist = distance((ball.x, ball.y), (player_x, player_y))
        if str(dist) != "nan":
            dists.append(distance((ball.x, ball.y), (player_x, player_y)))
    return dists

def get_team(team):
    x_columns = [c for c in team.keys() if c[-2:].lower()=='_x' and c!='ball_x'] # column header for player x positions
    x_columns.sort()
    y_columns = [c for c in team.keys() if c[-2:].lower()=='_y' and c!='ball_y'] # column header for player y positions
    y_columns.sort()
    vx_columns = ['{}_vx'.format(c[:-2]) for c in x_columns] # column header for player x positions
    vx_columns.sort()
    vy_columns = ['{}_vy'.format(c[:-2]) for c in y_columns] # column header for player y positions
    vy_columns.sort()
    speed_columns = ['{}_speed'.format(c[:-2]) for c in y_columns] # column header for player y positions
    speed_columns.sort()

    home_away = "Home"
    if(str(team.keys()[2][0:4]) == "Away"):
            home_away = "Away"

    players = []
    for x_col, y_col, vx_col, yv_col, speed_col in zip(x_columns, y_columns, vx_columns, vy_columns, speed_columns):
        name = x_col.split("_")[1]
        players.append(Player(team[x_col], team[y_col], team[vx_col], team[yv_col], team[speed_col], home_away, name))
    return players


