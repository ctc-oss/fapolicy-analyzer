from matplotlib.backends.backend_gtk3agg import \
    FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure
from fapolicy_analyzer.ui.reducers.stats_reducer import StatsStreamState

class ObjCacheView(object):
    def __init__(self):
        self._figure = Figure(figsize=(5, 4), dpi=100)
        self._ax = self._figure.add_subplot(1, 1, 1)

        self._hits, = self._ax.plot([], [], label="Hits")
        self._misses, = self._ax.plot([], [], label="Misses")

        self._ax.set_xticklabels([])
        self._ax.set_title('Object Cache')
        self._ax.legend()

        self.canvas = FigureCanvas(self._figure)
        self.canvas.set_size_request(100, 200)

    def show(self):
        self.canvas.show()

    def on_event(self, stats: StatsStreamState):
        self._hits.set_xdata(stats.ts.timestamps())
        self._hits.set_ydata(stats.ts.object_hits())
        self._misses.set_xdata(stats.ts.timestamps())
        self._misses.set_ydata(stats.ts.object_misses())
        self._ax.relim()
        self._ax.autoscale_view()
        self.canvas.draw()

class SubjCacheView(object):
    def __init__(self):
        self._figure = Figure(figsize=(5, 4), dpi=100)
        self._ax = self._figure.add_subplot(1, 1, 1)

        self._hits, = self._ax.plot([], [], label="Hits")
        self._misses, = self._ax.plot([], [], label="Misses")

        self._ax.set_xticklabels([])
        self._ax.set_title('Subject Cache')
        self._ax.legend()

        self.canvas = FigureCanvas(self._figure)
        self.canvas.set_size_request(100, 200)

    def show(self):
        self.canvas.show()

    def on_event(self, stats: StatsStreamState):
        self._hits.set_xdata(stats.ts.timestamps())
        self._hits.set_ydata(stats.ts.subject_hits())
        self._misses.set_xdata(stats.ts.timestamps())
        self._misses.set_ydata(stats.ts.subject_misses())
        self._ax.relim()
        self._ax.autoscale_view()
        self.canvas.draw()


class SlotsCacheView(object):
    def __init__(self):
        self._figure = Figure(figsize=(5, 4), dpi=100)
        self._ax = self._figure.add_subplot(1, 1, 1)

        self._oslots, = self._ax.plot([], [], label="Object")
        self._sslots, = self._ax.plot([], [], label="Subjects")

        self._ax.set_xticklabels([])
        self._ax.set_title('Slots Used')
        self._ax.legend()

        self.canvas = FigureCanvas(self._figure)
        self.canvas.set_size_request(100, 200)

    def show(self):
        self.canvas.show()

    def on_event(self, stats: StatsStreamState):
        self._oslots.set_xdata(stats.ts.timestamps())
        self._oslots.set_ydata(stats.ts.object_slots_in_use())
        self._sslots.set_xdata(stats.ts.timestamps())
        self._sslots.set_ydata(stats.ts.subject_slots_in_use())
        self._ax.relim()
        self._ax.autoscale_view()
        self.canvas.draw()


class EvictionCacheView(object):
    def __init__(self):
        self._figure = Figure(figsize=(5, 4), dpi=100)
        self._ax = self._figure.add_subplot(1, 1, 1)

        self._o, = self._ax.plot([], [], label="Object")
        self._s, = self._ax.plot([], [], label="Subject")

        self._ax.set_xticklabels([])
        self._ax.set_title('Cache Evictions')
        self._ax.legend()

        self.canvas = FigureCanvas(self._figure)
        self.canvas.set_size_request(100, 200)

    def show(self):
        self.canvas.show()

    def on_event(self, stats: StatsStreamState):
        self._o.set_xdata(stats.ts.timestamps())
        self._o.set_ydata(stats.ts.object_evictions())
        self._s.set_xdata(stats.ts.timestamps())
        self._s.set_ydata(stats.ts.subject_evictions())
        self._ax.relim()
        self._ax.autoscale_view()
        self.canvas.draw()
