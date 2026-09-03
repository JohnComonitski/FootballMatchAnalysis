from .xg import *
from .xt import *

def players_in_sequence(match, sequence):
    players = []
    players_names = []

    for possession in sequence["Possessions"]:
        player_name = possession["Player"]
        if player_name not in players_names:
            players_names.append(player_name)
            players.append(match.get_player(player_name))

    return players

def is_player_in_sequence(sequence, player):
    player_name = player
    if( str(type(player))) == "<class 'FootballMatchAnalysis.objects.player.Player'>":
        player_name = f"Player{player.name}"

    seen = False
    for possession in sequence["Possessions"]:
        if possession["Player"] == player_name:
            seen = True

    return seen

def events_in_sequence(match, sequence, shave_ends=True):
    start = sequence["StartFrame"]
    end = sequence["EndFrame"]
    team = sequence["Team"]
    events = match.events

    sequence_events = events[(
        (
            (events["Start Frame"] >= start) 
            | 
            (events["End Frame"] >= start)
        ) 
        & 
        (
            (events["Start Frame"] <= end)
            |
            (events["End Frame"] <= end)
        )
    )]

    if shave_ends:
        #Shave End
        for idx in range(len(sequence_events)):
            e = sequence_events.iloc[-1-idx]
            if e["Team"] == team:
                break

            shave = ["RECOVERY", "PASS", "BALL LOST"]
            if e["Type"] in shave:
                continue
            else: 
                break

        if idx > 0:
            sequence_events = sequence_events.iloc[0: len(sequence_events) - idx]

        #Shave Start
        for idx in range(len(sequence_events)):
            e = sequence_events.iloc[idx]
            if e["Team"] == team:
                break

        if idx > 0:
            sequence_events = sequence_events.iloc[idx: len(sequence_events)]

    return sequence_events

def sequence_xg(match, sequence):
    events = events_in_sequence(match, sequence)
    team = sequence['Team']
    final_event = events.iloc[-1]
    xg = 0
    if final_event["Type"] == "SHOT":

        invert = False
        if team != match.team_attacking_right():
            invert = True

        try:
            xg = get_xg((final_event["Start X"], final_event["Start Y"]), invert=invert)
        except:
            xg = get_xg((final_event["Start X"] + .1, final_event["Start Y"] + .1), invert=invert)

    return xg

def sequence_xt(match, sequence):
    events = events_in_sequence(match, sequence)
    team = sequence['Team']
    final_event = events.iloc[-1]

    invert = False
    if team != match.team_attacking_right():
        invert = True
        
    xt = 0
    try:
        xt = get_xt((final_event["Start X"], final_event["Start Y"]), invert=invert)
    except:
        xt = get_xt((final_event["Start X"] + .1, final_event["Start Y"] + .1), invert=invert)

    return xt