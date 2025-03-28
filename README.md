# Football Match Analysis

A Python library that utilize's Friend's of Tracking's [Metrica Tracking Data Library](https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking). This library makes the examples from Friend's of Tracking's [Tracking Data Tutorial Series](https://www.youtube.com/watch?v=8TrleFklEsE) easy acceible via easy to use objects & functions and expands on the functionality to make match analysis from football tracking & event data easy!

<!--TOC-->

- [Football Match Analysis](#footbal-match-analysis)
  - [Getting Started](#getting-started)
  - [Features](#features)
  - [Getting Tracking Data](#getting-tracking-data)
  - [Examples](#examples)
  - [Licenses](#license)


## Getting Started

1. Clone the repository

   ```shell
   git clone https://github.com/JohnComonitski/FootballMatchAnalysis.git
   ```

2. Move to the project directory

   ```shell
   cd FootballMatchAnalysis
   ```

3. Create and activate a Python
   [virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments).
   On GNU/Linux systems this is as easy as:

   ```shell
   python3 -m venv .venv
   . .venv/bin/activate
   # Work inside the environment.
   ```

4. Install the Python dependencies

   ```shell
   pip install -r requirements.txt
   ```

5. In your python script, import the supporting libraries

    ```python
    from analysis.event import *
    from analysis.player import *
    from events.match import Match
    ```

## Features
...

## Examples
### Calculate Distance Traveled by Each Player
Calculate the distance traveled in kilometers by every player in the match.

```python
from analysis.player import *
from events.match import Match

# Load Event Data
DATADIR = './data'
game_id = 2

track_distance_covered(match)
```


### Plot the Events and Locations of Players Moments Before a Goal
Plot the location of every player on the field the moment before the first goal and plot the passes that led up to the goal.

```python
from analysis.player import *
from events.match import Match

# Load Event Data
DATADIR = './data'
game_id = 2

match = Match(DATADIR, game_id)
goals = match.goals()
goal_frame = goals.iloc[1].name

plot_goal(match, goal_frame)
```


### Plot the Pitch Control For a Given Moment in a Match
Plot the location of every player on the field during a given moment of a match and describe who controls what sections of the pitch using a voronoi diagram.

```python
from analysis.event import *
from events.match import Match

# Load Event Data
DATADIR = './data'
game_id = 2

match = Match(DATADIR, game_id)
frame = 100

plot_pitch_control(match, frame)
```


## Licenses
MIT License
Copyright (c) 2025 John Comonitski