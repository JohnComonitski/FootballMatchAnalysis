import FootballMatchAnalysis.metrica.Metrica_IO as mio
import FootballMatchAnalysis.metrica.Metrica_Velocities as mvel
from FootballMatchAnalysis.objects.moment import Moment
from FootballMatchAnalysis.objects.player import Player
from FootballMatchAnalysis.objects.ball import Ball
from FootballMatchAnalysis.analysis.utils import *
import cv2

class Match:
    def __init__(self, DATADIR, game_id):
        self.datadir = DATADIR
        self.game_id = game_id

        # Data Prep and Processing
        events = mio.read_event_data(DATADIR,game_id)
        tracking_home = mio.tracking_data(DATADIR,game_id, 'Home')
        tracking_away = mio.tracking_data(DATADIR,game_id, 'Away')
        tracking_home = mio.to_metric_coordinates(tracking_home)
        tracking_away = mio.to_metric_coordinates(tracking_away)
        events = mio.to_metric_coordinates(events)
        tracking_home,tracking_away,events = mio.to_single_playing_direction(tracking_home,tracking_away,events)
        
        # Calculate Player Velocities
        tracking_home = mvel.calc_player_velocities(tracking_home,smoothing=True)
        tracking_away = mvel.calc_player_velocities(tracking_away,smoothing=True)

        self.events = events
        self.tracking_home = tracking_home
        self.tracking_away = tracking_away
        self.game_states = None
        self.time_on_ball = None
        self.get_time_on_ball()

    def event_types(self):
        return self.events['Type'].unique()

    def subevent_types(self, event_type):
        return self.events[self.events['Type']==event_type]['Subtype'].unique()

    def get_events(self, event_type):
        return self.events[self.events['Type']==event_type]
    
    def get_subtype_events(self, subevent_type):
        return self.events[self.events['Subtype']==subevent_type]
    
    def goals(self):
        shots = self.events[self.events.Type=='SHOT']
        return shots[shots['Subtype'].str.contains('-GOAL')]
    
    def players(self, team = None):
        if team == "Home":
            team = self.tracking_home.iloc[0]
            return players_to_list(team)
        elif team == "Away":
            team = self.tracking_away.iloc[0]
            return players_to_list(team)
        else:
            home = self.tracking_home.iloc[0]
            away = self.tracking_away.iloc[0]
            return players_to_list(home) + players_to_list(away)

    def get_event(self, frame):
        row = self.events[self.events["Start Frame"] == frame]

        if row.empty:
            return None
        else:
            return row.iloc[0]
    
    def get_moment(self, frame):
        time = round(int(frame) * 0.04, 2)
        state = self.current_state(time)

        events = self.events
        event = events[events["Start Frame"] == frame]
        if event.empty:
            event =  None
        else:
            event =  event.iloc[0]

        home = self.tracking_home
        home_players = home[home["Time [s]"] == round(frame*0.04, 2)]
        if home_players.empty:
            home_players =  None
        else:
            home_players =  home_players.iloc[0]

        away = self.tracking_away
        away_players = away[away["Time [s]"] == round(frame*0.04, 2)]
        if away_players.empty:
            away_players =  None
        else:
            away_players =  away_players.iloc[0]

        return Moment(frame, event, home_players, away_players, time, state)
    
    def home_team(self):
        return self.players(team="Home")

    def away_team(self):
        return self.players(team="Away")
    
    def ball(self):
        return Ball(None, None, None, None, None)

    def path(self, obj, start_frame=None, end_frame=None):
        if start_frame is None:
            start_frame = 1
        if end_frame is None:
            end_frame = len(self.tracking_home)

        x_col = "ball_x"
        y_col = "ball_y"
        tracking = self.tracking_home
        if "player" in str(type(obj)):
            x_col = f"{obj.team}_{obj.name}_x"
            y_col = f"{obj.team}_{obj.name}_y"
            if obj.team == "Away":
                tracking = self.tracking_away
        
        path = []
        for i in range(start_frame, end_frame):
            frame = tracking.iloc[i]
            path.append((frame[x_col], frame[y_col]))
        return path
    
    def get_game_states(self):
        shots = self.get_subtype_events("ON TARGET-GOAL")

        current_state = "0-0"
        game_states = { "0-0" : { "start" : 0, "end" : None } }
        for i, shot in shots.iterrows():
            time = shot["End Time [s]"]
            team = shot["Team"]
            home_goals = int(current_state.split("-")[0])
            away_goals = int(current_state.split("-")[1])
            if team == "Home":
                home_goals += 1
            else:
                away_goals += 1
            new_state = f"{home_goals}-{away_goals}"

            game_states[current_state]["end"] = time
            game_states[new_state] = { "start" : time, "end" : None }
            current_state = new_state

        self.game_states = game_states

    def current_state(self, time):
        if self.game_states is None:
            self.get_game_states()
        
        for state in self.game_states:
            if time >= self.game_states[state]["start"]:
                if self.game_states[state]["end"] is None:
                    return state
                
                if time <= self.game_states[state]["end"]:
                    return state

    def get_possessions(self):
        has_moment = True
        frame = 1
        while has_moment:
            moment = self.get_moment(frame)
            if moment is None:
                has_moment = False

    def get_time_on_ball(self, start=None, end=None, return_res=None):
        skip_events = [ "CHALLENGE", "SET PIECE", "CARD" ]

        possessions = []
        last_possession = {
            "StartFrame" : None,
            "EndFrame" : None,
            "Team" : None,
            "Player" : None,
        }
        current_possession = {
            "StartFrame" : None,
            "EndFrame" : None,
            "Team" : None,
            "Player" : None,
        }

        events = self.events
        if start and end:
            events = self.events.loc[start:end]

        for i, event in events.iterrows():
            if current_possession["StartFrame"] is None and ( event["Type"] not in skip_events ) and ( event["Type"] not in ["BALL LOST", "BALL OUT"] ):
                current_possession["Team"] = event["Team"]
                current_possession["Player"] = event["From"]
                current_possession["StartFrame"] = event["Start Frame"]

            else:
                if current_possession["StartFrame"] is None and ( event["Type"] not in skip_events ) and ( event["Type"] not in ["BALL LOST", "BALL OUT"] ):
                    current_possession["Team"] = event["Team"]
                    current_possession["Player"] = event["From"]
                    current_possession["StartFrame"] = event["Start Frame"] 

                if event["Type"] == "PASS":
                    last_event = events.iloc[i-1]
                    if last_event["Type"] == "SET PIECE" or event["Subtype"] == "GOAL KICK":
                        current_possession["StartFrame"] = event["Start Frame"]
                    
                    #Possesion of pass giver
                    current_possession["Team"] = event["Team"]
                    current_possession["Player"] = event["From"]
                    current_possession["EndFrame"] = event["Start Frame"]

                    last_possession = current_possession.copy()
                    possessions.append(last_possession)

                    #Possession of pass reciever
                    current_possession["Team"] = event["Team"]
                    current_possession["Player"] = event["To"]
                    current_possession["StartFrame"] = event["End Frame"]
                elif event["Type"] == "BALL LOST":
                    last_event = events.iloc[i-1]
                    if event["Subtype"] == "END HALF":
                        #Half is Over
                        current_possession["EndFrame"] = event["Start Frame"]
                        last_possession = current_possession.copy()
                        possessions.append(last_possession)

                        #Kick Start new ball sequence
                        current_possession = {
                            "StartFrame" : None,
                            "EndFrame" : None,
                            "Team" : None,
                            "Player" : None,
                        }
                    elif last_event["Type"] == "SET PIECE":
                        current_possession["Team"] = event["Team"]
                        current_possession["Player"] = event["From"]
                        current_possession["StartFrame"] = event["Start Frame"]

                        current_possession["EndFrame"] = event["Start Frame"]
                        last_possession = current_possession.copy()
                        possessions.append(last_possession)
                    elif(current_possession["Player"] == event["From"]):
                        current_possession["EndFrame"] = event["Start Frame"]
                        last_possession = current_possession.copy()
                        possessions.append(last_possession)
                elif event["Type"] == "RECOVERY":
                    last_event = events.iloc[i-1]
                    if event["Subtype"] == "THEFT" or last_event["Type"] != "BALL LOST":
                        #End Possession
                        current_possession["EndFrame"] = event["Start Frame"]

                        last_possession = current_possession.copy()
                        possessions.append(last_possession)

                    current_possession["Team"] = event["Team"]
                    current_possession["Player"] = event["From"]
                    current_possession["StartFrame"] = event["Start Frame"]
                elif event["Type"] == "CHALLENGE":
                    pass
                elif event["Type"] == "SET PIECE":
                    pass
                elif event["Type"] == "CARD":
                    pass
                elif event["Type"] ==  "FAULT RECEIVED":
                    #End of Possession
                    current_possession["EndFrame"] = event["Start Frame"]
                    last_possession = current_possession.copy()
                    possessions.append(last_possession)

                    #Kick Start new ball sequence
                    current_possession = {
                        "StartFrame" : None,
                        "EndFrame" : None,
                        "Team" : None,
                        "Player" : None,
                    }
                elif event["Type"] == "BALL OUT":

                    last_event = events.iloc[i-1]
                    #Free kick went out
                    if last_event["Type"] == "SET PIECE":
                        current_possession["Team"] = event["Team"]
                        current_possession["Player"] = event["From"]
                        current_possession["StartFrame"] = event["Start Frame"]

                    #End of Possession
                    current_possession["EndFrame"] = event["Start Frame"]
                    last_possession = current_possession.copy()
                    possessions.append(last_possession)

                    #Kick Start new ball sequence
                    current_possession = {
                        "StartFrame" : None,
                        "EndFrame" : None,
                        "Team" : None,
                        "Player" : None,
                    }
                elif event["Type"] == "SHOT":
                    #End of Possession
                    current_possession["EndFrame"] = event["Start Frame"]
                    last_possession = current_possession.copy()
                    possessions.append(last_possession)
                    
                    #Kick Start new ball sequence
                    current_possession = {
                        "StartFrame" : None,
                        "EndFrame" : None,
                        "Team" : None,
                        "Player" : None,
                    }

        if return_res:
            return possessions
        
        self.time_on_ball = possessions
    
    def whos_on_ball(self, frame_number):
        for possession in self.time_on_ball:
            if str(frame_number) == str(possession["StartFrame"]) and str(frame_number) == str(possession["EndFrame"]):
                return possession
            elif str(frame_number) >= str(possession["StartFrame"]) and str(frame_number) <= str(possession["EndFrame"]):
                return possession
            
    def generate_video(self, start_frame, end_frame, output_video="video.mp4"):
        moment = self.get_moment(start_frame)
        first_frame = moment.plot_moment()
        img = first_frame.cv2_image()
        height, width, layers = img.shape

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(output_video, fourcc, 24, (width, height))
        video.write(img)
        first_frame.close()

        for frame in range(start_frame+1, end_frame+1):
            moment = self.get_moment(frame)
            plot = moment.plot_moment()

            img = plot.cv2_image()
            video.write(img)
            plot.close()

        video.release()

    def get_event_index(self, event):
        matches = self.events.apply(lambda r: r.equals(event), axis=1)
        idx = self.events.index[matches]

        if len(idx) == 0:
            raise ValueError("Row not found in DataFrame")
        if len(idx) > 1:
            raise ValueError("Multiple matching rows found")

        return idx[0]