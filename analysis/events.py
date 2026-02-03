import metrica.Metrica_IO as mio
import metrica.Metrica_Viz as mviz
import metrica.Metrica_PitchControl as mpc
import numpy as np
from objects.plot import Plot
import matplotlib.pyplot as plt
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