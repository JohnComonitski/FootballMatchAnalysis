from FootballMatchAnalysis.analysis.utils import *

class Player:
    def __init__(self, x, y, vx, vy, speed, team, name=""):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = speed
        self.team = team
        self.name = name

    def coords(self):
        return (self.x, self.y)
    
    def coords_in_radius(self, radius=5):
        x = self.x
        y = self.y
        step = 1
        circumference_steps = {
            "1" : .45,
            "2" : .4,
            "3" : .35,
            "4" : .3,
            "5" : .25
        }

        points = []
        for r in range(step, radius+1, step):
            circumference_step = 1
            if str(r) in circumference_steps:
                circumference_step = circumference_steps[str(r)]
                
            res = circumference_points((x,y), r, circumference_step)
            for ps in res:
                points.append(ps)

        return points

    def to_dict(self):
        return {
            "name" : self.name,
            "team" : self.team
        }