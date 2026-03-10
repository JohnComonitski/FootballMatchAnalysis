import FootballMatchAnalysis.metrica.Metrica_IO as mio
import FootballMatchAnalysis.metrica.Metrica_Viz as mviz
import FootballMatchAnalysis.metrica.Metrica_PitchControl as mpc
from FootballMatchAnalysis.objects.plot import Plot
from FootballMatchAnalysis.analysis.utils import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Take an event and return True of event is a Key Pass
def is_key_pass(match, event):
    if event["Type"] != "PASS":
        return False

    idx = match.get_event_index(event)

    while True:
        idx +=1
        if 0 <= idx < len(match.events):
            event = match.events.iloc[idx]
            if event["Type"] == "SHOT":
                return True
            if event["Type"] in [ "PASS", "BALL LOST", "BALL OUT" "CARD" "SET PIECE", "FAULT RECEIVED" ]:
                return False
        else:
            return False

# For a given passing event, returns the previous pass
def previous_pass(match, event):
    if event["Type"] != "PASS":
        return None

    idx = match.get_event_index(event)
    while True:
        idx -= 1
        if 0 <= idx < len(match.events):
            prev_event = match.events.iloc[idx]

            if prev_event["Type"] == "PASS":
                if prev_event["To"] == event["From"]:
                    return prev_event
            else:
                return None
        else:
            return None
        
# For a given passing event, returns the previous pass
def next_pass(match, event):
    if event["Type"] != "PASS":
        return None

    idx = match.get_event_index(event)
    while True:
        idx +=1
        if 0 <= idx < len(match.events):
            event = match.events.iloc[idx]
            if event["Type"] == "PASS":
                return event
            if event["Type"] in [ "SHOT", "BALL LOST", "BALL OUT" "CARD" "SET PIECE", "FAULT RECEIVED" ]:
                return None
        else:
            return None

# If an event leads to a shot, returns the shot
def get_shot(match, event):
    idx = match.get_event_index(event)

    while True:
        idx +=1
        if 0 <= idx < len(match.events):
            next_event = match.events.iloc[idx]
            if next_event["Type"] == "SHOT":
                if next_event["From"] == event["To"]:
                    return next_event
            elif next_event["Type"] in [ "PASS", "BALL LOST", "BALL OUT" "CARD" "SET PIECE", "FAULT RECEIVED" ]:
                return None
        else:
            return None

def is_one_two(match, event):
    if event["Type"] != "PASS":
        return False

    from_player = event["From"]

    next_p = next_pass(match, event)
    if next_p is not None:
        if from_player == next_p["To"]:
            return True

    return False

def get_players_packed(match, event, relevance_distance=25):
    if event["Type"] != "PASS":
        return []
    
    before = match.get_moment(event["Start Frame"])
    after = match.get_moment(event["End Frame"])
    
    team_on_ball = before.possession(threshold=100).team
    players_off_ball = before.home_team()
    if team_on_ball == "Home":
        players_off_ball = before.away_team()

    #Make Sure Ball makes forward progress
    start_x = event["Start X"]
    end_x = event["End X"]
    dif = end_x - start_x
    if team_on_ball == "Away" and dif > 0:
        return []
    elif team_on_ball == "Home" and dif < 0:
        return []

    # Who is behind the ball before pass
    ball_x = before.ball.x
    behind_the_ball_before = []
    for player in players_off_ball:
        loc = player.x
        if str(loc) != "nan":
            if team_on_ball == "Home":
                if player.x < ball_x:
                    behind_the_ball_before.append(player)
            elif team_on_ball == "Away":
                if player.x > ball_x:
                    behind_the_ball_before.append(player)

    # Who is behind the ball after pass
    players_off_ball = after.home_team()
    if team_on_ball == "Home":
        players_off_ball = after.away_team()
        
    ball_x = after.ball.x
    behind_the_ball_after = []
    for player in players_off_ball:
        loc = player.x
        if str(loc) != "nan":
            if team_on_ball == "Home":
                if player.x < ball_x:
                    behind_the_ball_after.append(player)
            elif team_on_ball == "Away":
                if player.x > ball_x:
                    behind_the_ball_after.append(player)

    #Ignore player's too far away
    final_before_list = []
    final_before_list_names = []
    for p in behind_the_ball_before:
        dist = distance((p.x, p.y), (after.ball.x, after.ball.y))
        if dist < relevance_distance:
            final_before_list.append(p)
            final_before_list_names.append(p.name)
    
    final_after_list = []
    for p in behind_the_ball_after:
        if p.name not in final_before_list_names:
            dist = distance((p.x, p.y), (after.ball.x, after.ball.y))
            if dist < relevance_distance:
                final_after_list.append(p)

    return final_after_list

def players_packed(match, event, relevance_distance=25):
    return len(get_players_packed(match, event, relevance_distance))

def events_by_player(match, player, type=None, subtype=None, to=None ):
    if type is None:
        return None

    events = match.events
    if type not in match.event_types():
        return None
    
    events = events[events["Type"] == type]
    if subtype:
        if subtype not in match.subevent_types(type):
            return None
        events = events[events["Subtype"] == subtype]

    if type in ["PASS", "BALL LOST"]:
        events = events[events["From"] == f"Player{player.name}"]
        if to:
            events = events[events["To"] == f"Player{player.name}"]
    
    return events


