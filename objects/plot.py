from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import math
import metrica.Metrica_IO as mio
import metrica.Metrica_Viz as mviz
import matplotlib.pyplot as plt
from analysis.xt import *
from analysis.xg import *

class Plot:
    def __init__(self, fig = None, ax = None):
        self.field_dimen = (106.0,68)
        if not fig:
            fig, ax = mviz.plot_pitch( field_dimen = self.field_dimen )

        self.fig = fig
        self.ax = ax
        self.name = "plot.png"

    def close(self):
        plt.close(self.fig)

    def write(self, text, x, y, font_size=12, c="#000000", justifification = 'center'):
        self.ax.text( x, y, text, ha=justifification, va='center', fontsize=font_size, color=c)

    def print(self, name=None):
        if not name:
            name = self.name
        self.fig.savefig(name, format="png", bbox_inches="tight")

    def draw_point(self, x, y, c="#000000", s=5, alpha=1):
        self.ax.scatter(x, y, s=s, color=c, alpha=alpha)

    def draw_box(self, rect, c="#000000", alpha=1):
        tl, tr, bl, br = rect

        self.ax.plot([tl[0], tr[0]], [tl[1], tr[1]], color=c, linewidth=2, alpha=alpha)
        self.ax.plot([tr[0], br[0]], [tr[1], br[1]], color=c, linewidth=2, alpha=alpha)
        self.ax.plot([br[0], bl[0]], [br[1], bl[1]], color=c, linewidth=2, alpha=alpha)
        self.ax.plot([bl[0], tl[0]], [bl[1], tl[1]], color=c, linewidth=2, alpha=alpha)

    def draw_line(self, p1, p2, c="#000000", alpha=1):
        self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=c, linewidth=1, alpha=alpha)

    def draw_circle(self, x, y, r, c="#000000", alpha=1):
        circle = plt.Circle((x, y), r, fill=False)
        self.ax.add_patch(circle, alpha=alpha)
        self.ax.set_aspect('equal', 'box')

    def draw_path(self, path, c="#000000", alpha=1):
        for i in range(0, len(path)):
            if str(path[i][0]) != "nan":
                self.draw_point(path[i][0], path[i][1], c, s=1, alpha=alpha)

    def draw_heat_map(self, path):
        path = [
            (x, y)
            for (x, y) in path
            if not (math.isnan(x) or math.isnan(y))
        ]
        xs = [p[0] for p in path]
        ys = [p[1] for p in path]

        cmap = LinearSegmentedColormap.from_list('custom_cmap', ['mediumseagreen', 'yellow', 'orange','red'])

        self.ax.hist2d(
            xs,
            ys,
            bins=100,
            range=[[self.ax.get_xlim()[0], self.ax.get_xlim()[1]],
                [self.ax.get_ylim()[0], self.ax.get_ylim()[1]]],
            cmap=cmap,
            vmin=0,
            vmax=400,
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.ax.set_frame_on(False)

    def draw_xt(self, invert=False):
        zones = xt_map_zones()
        for zone_id in zones:
            zone = zones[zone_id]
            if invert:
                new_zone = []
                for coord in zone:
                    new_zone.append([ coord[0] * -1, coord[1] * -1, ])
                zone = new_zone
            self.draw_box(zone)

            xt = zone_to_xt(zone_id)
            x = zone[0][0] - ((zone[0][0] - zone[2][0]) / 2 )
            y = zone[0][1] - ((zone[0][1] - zone[1][1]) / 2 )
            self.write(xt, x=x, y=y, c="#000000")

    def draw_xg(self, invert=False):
        zones = xg_map_zones()
        for zone_id in zones:
            zone = zones[zone_id]
            if invert:
                new_zone = []
                for coord in zone:
                    new_zone.append([ coord[0] * -1, coord[1] * -1, ])
                zone = new_zone
            self.draw_box(zone)

            xg = zone_to_xg(zone_id)
            x = zone[0][0] - ((zone[0][0] - zone[2][0]) / 2 )
            y = zone[0][1] - ((zone[0][1] - zone[1][1]) / 2 )
            self.write(xg, x=x, y=y, c="#000000")

    def cv2_image(self):
        canvas = FigureCanvas(self.fig)
        canvas.draw()

        buf = np.frombuffer(canvas.tostring_rgb(), dtype=np.uint8)
        w, h = self.fig.canvas.get_width_height()
        img = buf.reshape((h, w, 3))

        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    def draw_event(self, event, c='r', alpha = 0.5,):
        figax = (self.fig, self.ax)

        indicator = "Marker"
        if( event["Type"] in [ "PASS", "SHOT" ] ):
            indicator = "Arrow"

        if( event["Type"] == "BALL LOST" and event["Subtype"] == "INTERCEPTION" ):
            indicator = [ "Arrow", "X" ]

        fig,ax = mviz.plot_event(frame=event, figax=figax, indicators=indicator, annotate=False, alpha = alpha, field_dimen = self.field_dimen, color = c )
        self.fig = fig
        self.ax = ax