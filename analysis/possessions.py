from FootballMatchAnalysis.analysis.zones import *
from FootballMatchAnalysis.analysis.utils import *

def is_valid_possession(possession):
    if possession["Player"] is None:
        return False
    
    start = possession["StartFrame"]
    end = possession["EndFrame"]
    if start is None or end is None:
        return False

    return True

def is_touch(match, possession, player=None):
    if is_valid_possession(possession) == False:
        return False

    if player == None:
        player = match.get_player(possession["Player"])

    start = possession["StartFrame"]
    end = possession["EndFrame"]

    if int(end) - int(start) < 24:
        return True

    return False
    
def is_progressive_carry(match, possession, player=None):
    if is_valid_possession(possession) == False:
        return False

    if player == None:
        player = match.get_player(possession["Player"])

    start = possession["StartFrame"]
    end = possession["EndFrame"]

    if int(end) - int(start) < 24:
        return False

    start_event = match.get_event(start, from_player=possession["Player"])
    if start_event is None:
        start_event = match.get_event(start, to_player=possession["Player"])

    end_event = match.get_event(end, from_player=possession["Player"])

    if start_event is None or end_event is None:
        return False

    start_x = start_event["Start X"]
    if str(start_event["End X"]) != "nan":
        start_x = start_event["End X"]

    end_x = end_event["Start X"]

    is_attacking_right = match.is_attacking_right(player)
    if is_attacking_right:
        if end_x < start_x:
            return False
    else:
        if end_x > start_x:
            return False

    dist = round(abs(int(end_x) - int(start_x)), 2)
    if dist >= 10:
        return True
    
    return False

def is_carry(match, possession, player=None):
    if is_valid_possession(possession) == False:
        return False

    if player == None:
        player = match.get_player(possession["Player"])

    start = possession["StartFrame"]
    end = possession["EndFrame"]

    if int(end) - int(start) < 24:
        return False

    start_event = match.get_event(start, from_player=possession["Player"])
    if start_event is None:
        start_event = match.get_event(start, to_player=possession["Player"])

    end_event = match.get_event(end, from_player=possession["Player"])

    if start_event is None or end_event is None:
        return False

    start_x = start_event["Start X"]
    start_y = start_event["Start Y"]
    if str(start_event["End X"]) != "nan":
        start_x = start_event["End X"]
        start_y = start_event["End Y"]

    end_x = end_event["Start X"]
    end_y = end_event["Start Y"]

    dist = distance((start_x, start_y), (end_x, end_y))
    if dist >= 5:
        return True
    
def possession_to_event(match, possession, player=None):
    if is_valid_possession(possession) == False:
        return None
    
    if player == None:
        player = match.get_player(possession["Player"])
    elif str(type(player)) == "<class 'str'>":
        player = match.get_player(player)

    subtype = None
    if is_carry(match, possession, player):
        subtype = "CARRY"
        if is_progressive_carry(match, possession, player):
            subtype = "PROGRESSIVE-CARRY"
    elif is_touch(match, possession, player):
        subtype = "TOUCH"
        
    start = possession["StartFrame"]
    start_time = round(start / 24, 2)
    end = possession["EndFrame"]
    end_time = round(end / 24, 2)

    start_event = match.get_event(start, from_player=player)
    if start_event is None:
        start_event = match.get_event(start, to_player=player)

    end_event = match.get_event(end, from_player=player)

    if start_event is None or end_event is None:
        return None 
    
    start_x = start_event["Start X"]
    start_y = start_event["Start Y"]
    if str(start_event["End X"]) != "nan":
        start_x = start_event["End X"]
        start_y = start_event["End Y"]

    end_x = end_event["Start X"]
    end_y = end_event["Start Y"]

    event = {
        "Team": possession["Team"],
        "Type": "POSSESSION",
        "Subtype": subtype,
        "Period": possession["Period"],
        "Start Frame": start,
        "Start Time [s]": start_time,
        "End Frame": end,
        "End Time [s]": end_time,
        "From": f"Player{possession['Player']}",
        "To": None,
        "Start X": start_x,
        "Start Y": start_y,
        "End X": end_x,
        "End Y": end_y,
        "Details" : ""
    }

    if "Match" in possession:
        event["Match"] = possession["Match"]

    return event

def get_player_possessions(match, player):
    possessions = []

    if str(type(player)) != "<class 'str'>":
        player = f"Player{player.name}"

    for possession in match.time_on_ball:
        if possession["StartFrame"] is None or possession["EndFrame"] is None or possession["Player"] is None:
            continue

        if possession["Player"] != player:
            continue

        start = possession["StartFrame"]
        end = possession["EndFrame"]
        if (end - start) > 360:
            continue

        possessions.append(possession)

    return possessions

def get_team_possessions(match, team):
    possessions = []

    for possession in match.time_on_ball:
        if possession["StartFrame"] is None or possession["EndFrame"] is None or possession["Player"] is None:
            continue

        if possession["Team"] != team:
            continue

        start = possession["StartFrame"]
        end = possession["EndFrame"]
        if (end - start) > 360:
            continue

        possessions.append(possession)

    return possessions

def get_possession(match, frame):
    for possession in match.time_on_ball:
        if possession["StartFrame"] is None or possession["EndFrame"] is None:
            continue

        start = possession["StartFrame"]
        end = possession["EndFrame"]

        if frame >= start and frame <= end:
            return possession

    return None

def get_next_possession(match, possession):
    i = 0
    for possible_possession in match.time_on_ball:
        if possible_possession["StartFrame"] is None or possible_possession["EndFrame"] is None:
            i+=1
            continue

        start = possible_possession["StartFrame"]
        end = possible_possession["EndFrame"]

        if possession["StartFrame"] == start and possession["EndFrame"] == end:
            if i+1 < len(match.time_on_ball):
                return match.time_on_ball[i+1]
        
        i+=1

    return None

def how_possession_ends(match, possession):
    if is_valid_possession(possession) == False:
        return None

    end_moment = match.get_moment(possession["EndFrame"])
    return end_moment.event

def does_possession_end_positively(match, possession):
    event = how_possession_ends(match, possession)
    if event is None:
        return None
    
    how_it_ended = f"{event["Type"]}/{event["Subtype"]}"

    if "PASS" in how_it_ended:
        return True
    elif how_it_ended in ['BALL LOST/HEAD-INTERCEPTION', 'BALL LOST/HEAD', 'BALL LOST/DEEP BALL', 'BALL LOST/INTERCEPTION', 'BALL LOST/CROSS-INTERCEPTION', 'BALL LOST/REFEREE HIT', 'BALL LOST/GOAL KICK']:
        return False
    elif "BALL OUT" in how_it_ended:
        return False
    elif "SHOT" in how_it_ended:
        return True
    elif how_it_ended in ['BALL LOST/nan',]:
        return False
    elif how_it_ended in ['BALL LOST/FORCED', 'CHALLENGE/TACKLE-LOST','CHALLENGE/GROUND-LOST','CHALLENGE/TACKLE-FAULT-LOST','BALL LOST/THEFT']:
        return False
    elif how_it_ended in ['FAULT RECEIVED/nan','CHALLENGE/GROUND-FAULT-WON','CHALLENGE/TACKLE-FAULT-WON']:
        return True
    elif how_it_ended in ['BALL LOST/CLEARANCE']:
        return True
