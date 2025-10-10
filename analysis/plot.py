import metrica.Metrica_IO as mio
import metrica.Metrica_Viz as mviz

class Plot:
    def __init__(self, fig = None, ax = None):
        if not fig:
            fig, ax = mviz.plot_pitch( field_dimen = (106.0,68) )

        self.fig = fig
        self.ax = ax
        self.name = "plot.png"

    def write(self, text, x, y, font_size=12, c="#000000"):
        self.ax.text( x, y, text, ha='center', va='center', fontsize=font_size, color=c)

    def print(self, name=None):
        if not name:
            name = self.name
        self.fig.savefig(name, format="png", bbox_inches="tight")

    def draw_box(self, rect, c="#000000"):
        tl, tr, bl, br = rect

        self.ax.plot([tl[0], tr[0]], [tl[1], tr[1]], color=c, linewidth=2)
        self.ax.plot([tr[0], br[0]], [tr[1], br[1]], color=c, linewidth=2)
        self.ax.plot([br[0], bl[0]], [br[1], bl[1]], color=c, linewidth=2)
        self.ax.plot([bl[0], tl[0]], [bl[1], tl[1]], color=c, linewidth=2)