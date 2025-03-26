import metrica.Metrica_IO as mio
import metrica.Metrica_Velocities as mvel

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
        tracking_home,tracking_away,events = mio.to_single_playing_direction(tracking_home,tracking_away,events)
        
        # Calculate Player Velocities
        tracking_home = mvel.calc_player_velocities(tracking_home,smoothing=True)
        tracking_away = mvel.calc_player_velocities(tracking_away,smoothing=True)

        self.events = events
        self.tracking_home = tracking_home
        self.tracking_away = tracking_away

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