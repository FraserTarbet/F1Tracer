import pyglet


class AnimationManager():
    def __init__(self, window, track_to_start_finish=False):
        self.window = window
        self.traces = []
        self.racing_line = None
        self.start_finish_point = None
        self.track_to_start_finish = track_to_start_finish
        self.cumulative_dt = 0
        self.ended_traces = []
        self.tracked_traces = []
        self.view_centre = None
        self.view_scale = 1000
        self.view_border = 60
        self.minimap = None

    def run(self):
        self.start()

    def update_traces(self, dt):
        self.cumulative_dt += dt

        # Update view position attribute (will always lag a frame behind traces, not a problem)
        if self.view_centre is None and len(self.tracked_traces) == 0:
            # Centre and scale to cover all traces
            mins = []
            maxs = []
            for trace in self.traces:
                mins.append((min(trace.x_tuple), min(trace.y_tuple)))
                maxs.append((max(trace.x_tuple), max(trace.y_tuple)))

            min_x = None
            min_y = None
            max_x = None
            max_y = None
            for i in range(len(self.traces)):
                if min_x is None or mins[i][0] < min_x:
                    min_x = mins[i][0]
                if min_y is None or mins[i][1] < min_y:
                    min_y = mins[i][1]
                if max_x is None or maxs[i][0] > max_x:
                    max_x = maxs[i][0]
                if max_y is None or maxs[i][1] > max_y:
                    max_y = maxs[i][1]

            self.view_centre = ((min_x + max_x) / 2, (min_y + max_y) / 2)
            self.view_scale = max(max_x - min_x, max_y - min_y)
            self.view_scale += self.view_scale * self.window.width / (self.window.width + self.view_border)

        tracked_count = len(self.tracked_traces)
        if tracked_count == 1:
            if self.tracked_traces[0].trackable:
                self.view_centre = self.tracked_traces[0].world_position
            else:
                self.view_centre = self.start_finish_point.world_point
        elif tracked_count > 1:
            x_sum = 0
            y_sum = 0
            for trace in self.tracked_traces:
                if trace.trackable:
                    x, y = trace.world_position
                else:
                    x, y = self.start_finish_point.world_point
                x_sum += x
                y_sum += y
            self.view_centre = (x_sum / tracked_count, y_sum / tracked_count)


        # Update traces
        for trace in self.traces:
            trace.update_position(self.cumulative_dt)
        for trace in self.ended_traces:
            if trace in self.traces:
                self.traces.remove(trace)
            if len(self.traces) == 0:
                #pyglet.app.exit()
                self.start()
                return

        if self.racing_line is not None:
            self.racing_line.update_position(self.cumulative_dt)

        if self.start_finish_point is not None:
            self.start_finish_point.update_position()

        if self.minimap is not None:
            self.minimap.update_position()


    def fit_to_viewport(self, world_x, world_y):
        coords = [None, None]
        for i, world_coord in enumerate([world_x, world_y]):
            coords[i] = world_coord - self.view_centre[i]
            coords[i] = (coords[i] * (self.window.width / self.view_scale) + self.window.width / 2)

        return coords

    def start(self):
        for trace in self.ended_traces:
            trace.restart()
        self.ended_traces.clear()

        animation_starts = []
        for trace in self.traces:
            animation_starts.append(min(trace.time_tuple))
        self.cumulative_dt = min(animation_starts)

        self.racing_line.start()
