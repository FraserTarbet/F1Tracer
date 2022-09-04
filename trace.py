import pyglet


class AnimationManager():
    def __init__(self):
        self.traces = []
        self.cumulative_dt = 0
        self.ended_traces = []

    def update_traces(self, dt):
        self.cumulative_dt += dt
        for trace in self.traces:
            trace.update_position(self.cumulative_dt)
        for trace in self.ended_traces:
            if trace in self.traces:
                self.traces.remove(trace)
            if len(self.traces) == 0:
                pyglet.app.exit()


class Trace(pyglet.shapes.Circle):
    def __init__(self, batch, radius, color, frame, animation_manager=None):
        x, y = frame[["X_fit", "Y_fit"]].iloc[0]
        super().__init__(200, 200, radius, color=color, batch=batch)
        self.time_tuple = tuple(frame["AnimTime"])
        self.x_tuple = tuple(frame["X_fit"])
        self.y_tuple = tuple(frame["Y_fit"])
        self.index = 0
        self.animation_manager = animation_manager
        if self.animation_manager is not None:
            self.animation_manager.traces.append(self)

    def update_position(self, cumulative_dt):
        # Increment index if needed
        if cumulative_dt >= self.time_tuple[self.index + 1]:
            self.index += 1
            # End trace when out of samples
            if self.index + 1 >= len(self.time_tuple):
                self.animation_manager.ended_traces.append(self)
                self.visible = False
                return

        # Interpolate X & Y coords based on where cumulative dt falls between samples
        prev_time = self.time_tuple[self.index]
        next_time = self.time_tuple[self.index + 1]
        interp_factor = (cumulative_dt - prev_time) / (next_time - prev_time)

        prev_x = self.x_tuple[self.index]
        next_x = self.x_tuple[self.index + 1]
        prev_y = self.y_tuple[self.index]
        next_y = self.y_tuple[self.index + 1]

        interp_x = prev_x + ((next_x - prev_x) * interp_factor)
        interp_y = prev_y + ((next_y - prev_y) * interp_factor)
        # interp_x = prev_x
        # interp_y = prev_y

        self.position = (interp_x, interp_y)


class RacingLine():
    def __init__(self, batch, width, color, frame):
        self.lines = []
        x_tuple = tuple(frame["X_fit"])
        y_tuple = tuple(frame["Y_fit"])
        for i in range(len(x_tuple) - 1):
            line = pyglet.shapes.Line(
                x=x_tuple[i], 
                y=y_tuple[i], 
                x2=x_tuple[i+1],             
                y2=y_tuple[i+1],
                width=width,
                color=color,
                batch=batch
            )
            self.lines.append(line)
