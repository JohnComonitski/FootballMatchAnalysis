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

    start_event = how_possession_starts(match, possession)
    end_event = how_possession_ends(match, possession)

    if start_event is None or end_event is None:
        return None 

    start_point = possession_starting_location(match, possession)
    end_point = possession_ending_location(match, possession)
    
    if start_point is None or end_point is None:
        return None 
    
    start_x = start_point[0]
    end_x = end_point[0]

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

    start_event = how_possession_starts(match, possession)
    end_event = how_possession_ends(match, possession)

    if start_event is None or end_event is None:
        return None 

    start_point = possession_starting_location(match, possession)
    end_point = possession_ending_location(match, possession)
    
    if start_point is None or end_point is None:
        return None 
    
    start_x = start_point[0]
    start_y = start_point[1]
    end_x = end_point[0]
    end_y = end_point[1]

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

    start_event = how_possession_starts(match, possession)
    end_event = how_possession_ends(match, possession)

    if start_event is None or end_event is None:
        return None 

    start_point = possession_starting_location(match, possession)
    end_point = possession_ending_location(match, possession)
    
    if start_point is None or end_point is None:
        return None 
    
    start_x = start_point[0]
    start_y = start_point[1]
    end_x = end_point[0]
    end_y = end_point[1]

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

def possession_events(match, possession):
    start_frame = possession["StartFrame"]
    end_frame = possession["EndFrame"]

    events = match.events
    events = events[(((events["Start Frame"] >= start_frame) | (events["End Frame"] >= start_frame)) & ((events["End Frame"] <= end_frame) | (events["Start Frame"] <= end_frame)))]

    return events

def how_possession_starts(match, possession):
    if is_valid_possession(possession) == False:
        return None

    starting_event_types = ["PASS", "RECOVERY", "SET PIECE"]

    start_frame = possession["StartFrame"]

    events = match.events
    possible_events = events[(events["Start Frame"] == start_frame) | (events["End Frame"] == start_frame)]
    possible_events = possible_events[((possible_events["From"] == possession["Player"]) | (possible_events["To"] == possession["Player"]))]

    if(len(possible_events) == 0):
        possible_events = events[(events["Start Frame"] == start_frame) | (events["End Frame"] == start_frame)]
        
    if(len(possible_events) == 0):
        return None

    if(len(possible_events) == 1):
        event = possible_events.iloc[0]
        if event["Type"] not in starting_event_types:
            return None
        return possible_events.iloc[0]

    for i, event in possible_events.iterrows():
        if event["Type"] in starting_event_types:
            return event

    return possible_events.iloc[0]

def how_possession_ends(match, possession):
    if is_valid_possession(possession) == False:
        return None

    ending_event_types = ["PASS", "BALL LOST", "BALL OUT", "SHOT", "FAULT RECEIVED"] 

    end_frame = possession["EndFrame"]

    events = match.events
    possible_events = events[(events["Start Frame"] == end_frame)]
    possible_events = possible_events[((possible_events["From"] == possession["Player"]) | (possible_events["To"] == possession["Player"]))]

    if(len(possible_events) == 0):
        return None

    if(len(possible_events) == 1):
        event = possible_events.iloc[0]
        if event["Type"] not in ending_event_types:
            return None

        return event

    for i, event in possible_events.iterrows():
        if event["Type"] in ending_event_types:
            return event

    all_events = possession_events(match, possession)
    for i, event in all_events.iterrows():
        if event["Type"] in ending_event_types:
            return event

    return possible_events.iloc[-1]

def possession_starting_location(match, possession):
    event = how_possession_starts(match, possession)

    if event is None:
        return None

    if event["Type"] in ["PASS"]:
        return ( event["End X"], event["End Y"] )
    else:
        return ( event["Start X"], event["Start Y"] )

def possession_ending_location(match, possession):
    event = how_possession_ends(match, possession)

    if event is None:
        return None

    return ( event["Start X"], event["Start Y"] )

def does_possession_end_positively(match, possession):
    event = how_possession_ends(match, possession)
    if event is None:
        return None
    
    how_it_ended = f"{event['Type']}/{event['Subtype']}"

    if "PASS" in how_it_ended:
        return True
    elif how_it_ended in ['BALL LOST/HEAD-INTERCEPTION', 'BALL LOST/HEAD', 'BALL LOST/DEEP BALL', 'BALL LOST/INTERCEPTION', 'BALL LOST/CROSS-INTERCEPTION', 'BALL LOST/REFEREE HIT', 'BALL LOST/GOAL KICK']:
        return False
    elif "BALL OUT" in how_it_ended:
        return False
    elif "SHOT" in how_it_ended:
        return True
    elif how_it_ended in ['BALL LOST/nan']:
        return False
    elif how_it_ended in ['BALL LOST/FORCED', 'CHALLENGE/TACKLE-LOST','CHALLENGE/GROUND-LOST','CHALLENGE/TACKLE-FAULT-LOST','BALL LOST/THEFT']:
        return False
    elif how_it_ended in ['FAULT RECEIVED/nan','CHALLENGE/GROUND-FAULT-WON','CHALLENGE/TACKLE-FAULT-WON']:
        return True
    elif how_it_ended in ['BALL LOST/CLEARANCE']:
        return True

def previous_possession(match, possession):
    possessions = match.time_on_ball
    idx = possession["Index"]

    if idx == 0:
        return None

    return possessions[idx-1]

def next_possession(match, possession):
    possessions = match.time_on_ball
    idx = possession["Index"]

    if idx == len(possessions):
        return None

    return possessions[idx+1]

def starts_with_dead_ball(match, possession):
    event = how_possession_starts(match, possession)

    if event is None:
        return False

    if event["Type"] == "SET PIECE":
        return True

    if event["Subtype"] == "GOAL KICK":
        return True
        
    return False

def starts_with_live_ball(match, possession):
    return not starts_with_live_ball(match, possession)