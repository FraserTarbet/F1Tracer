import pyglet


def hex_to_rgb(hex_string):
    return tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4))


class Trace(pyglet.shapes.Circle):
    def __init__(self, batch, group, radius, frame, animation_manager, tracking_window=None, tla=False, tcam=False, tail=False):
        super().__init__(200, 200, radius, batch=batch, group=group)
        self.color = hex_to_rgb(frame["TeamColour"].iloc[0])
        self.time_tuple = tuple(frame["AnimTime"])
        self.x_tuple = tuple(frame["X"])
        self.y_tuple = tuple(frame["Y"])
        self.index = 0
        self.animation_manager = animation_manager
        self.world_position = (0, 0)
        self.animation_manager.traces.append(self)

        self.tracking_window = tracking_window
        if tracking_window is not None:
            self.use_tracking_window = True
            self.trackable = False
        else:
            self.use_tracking_window = False
            self.trackable = True

        self.tla = tla
        if tla:
            self.tla = TraceLabel(self, frame["Tla"].iloc[0], self.color + (255, ), (10, 10), batch, group)

        if tcam:
            self.tcam = pyglet.shapes.Circle(0, 0, radius/2, color=(255, 255, 0), batch=batch, group=group)
        else:
            self.tcam = None

        self.tail = tail
        if tail:
            self.tail_last_dt = 0
            self.tail_last_point = None
    

    def restart(self):
        self.index = 0
        self.visible = True
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

        # Update tracking variable if used
        if self.use_tracking_window:
            self.trackable = self.tracking_window[0] <= cumulative_dt <= self.tracking_window[1]

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

        # Adjust to viewport
        self.world_position = (interp_x, interp_y)
        fit_to_viewport = self.animation_manager.fit_to_viewport(interp_x, interp_y)
        self.position = fit_to_viewport

        # Adjust any label
        if self.tla:
            self.tla.update_position()

        # Adjust any T-cam
        if self.tcam:
            self.tcam.position = self.position

        # Update any tail
        if self.tail:
            if self.tail_last_point is None:
                self.tail_last_point = self.world_position
                self.tail_last_dt = cumulative_dt
            elif cumulative_dt - self.tail_last_dt > 0.1:
                tail_section = TailSection(
                    self.tail_last_point[0], 
                    self.tail_last_point[1], 
                    self.world_position[0],
                    self.world_position[1],
                    self.radius,
                    self.color,
                    self._batch,
                    self._group,
                    self.animation_manager,
                    cumulative_dt
                )
                self.animation_manager.tail_sections.append(tail_section)
                self.tail_last_point = self.world_position
                self.tail_last_dt = cumulative_dt


class RacingLine():
    def __init__(self, batch, width, color, frame):
        self.lines = []
        x_tuple = tuple(frame["X"])
        y_tuple = tuple(frame["Y"])
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


class RollingRacingLine():
    def __init__(self, batch, group, width, color, frame, rolling_samples, animation_manager):
        self.animation_manager = animation_manager
        self.animation_manager.racing_line = self
        self.time_tuple = tuple(frame["AnimTime"])
        self.x_tuple = tuple(frame["X"])
        self.y_tuple = tuple(frame["Y"])
        self.index = 0
        self.rolling_samples = rolling_samples
        self.width = width
        self.color = color
        self.batch = batch
        self.group = group

        self.lines = []
        self.line_world_positions = []

        self.start()


    def start(self):
        self.index = 0
        self.lines = []
        self.line_world_positions = []
        for i in range(self.rolling_samples):
            new_line = pyglet.shapes.Line(
                x=0,
                y=0,
                x2=0,
                y2=0,
                width=self.width,
                color=self.color,
                batch=self.batch,
                group=self.group
            )
            self.lines.append(new_line)
            self.line_world_positions.append((0, 0, 0, 0))

        for i in range(int(self.rolling_samples / 2)):
            line_world_position = self.line_world_positions.pop(0)
            line_world_position = (self.x_tuple[i], self.y_tuple[i], self.x_tuple[i+1], self.y_tuple[i+1])
            self.line_world_positions.append(line_world_position)
            self.index += 1


    def update_position(self, cumulative_dt):
        # Roll through lines
        # Increment index if needed
        if cumulative_dt >= self.time_tuple[self.index - int(self.rolling_samples / 2)]:
            # End rolling when out of samples, but don't stop repositioning existing lines
            if self.index + 1 >= len(self.time_tuple):
                pass
            else:
                line_world_position = self.line_world_positions.pop(0)
                line_world_position = (self.x_tuple[self.index], self.y_tuple[self.index], self.x_tuple[self.index+1], self.y_tuple[self.index+1])
                self.line_world_positions.append(line_world_position)
                self.index += 1

        # Adjust all lines to viewport
        for i, line in enumerate(self.lines):
            coords_1 = self.animation_manager.fit_to_viewport(self.line_world_positions[i][0], self.line_world_positions[i][1])
            coords_2 = self.animation_manager.fit_to_viewport(self.line_world_positions[i][2], self.line_world_positions[i][3])
            line.position = (coords_1[0], coords_1[1], coords_2[0], coords_2[1])

        
class StartFinishPoint():
    def __init__(self, world_point, radius, color, batch, group, animation_manager):
        self.animation_manager = animation_manager
        self.animation_manager.start_finish_point = self
        self.world_point = world_point
        self.point = pyglet.shapes.Circle(0, 0, radius, color=color, batch=batch, group=group)

    def update_position(self):
        self.point.position = self.animation_manager.fit_to_viewport(self.world_point[0], self.world_point[1])


class TraceLabel(pyglet.text.Label):
    def __init__(self, parent_trace, text, color, offset, batch=None, group=None):
        super().__init__(text=text, font_name="TitilliumWeb-Regular", font_size=10, bold=True, color=color, batch=batch, group=group)
        self.parent_trace = parent_trace
        self.offset = offset

    def update_position(self):
        self.position = (self.parent_trace.position[0] + self.offset[0], self.parent_trace.position[1] + self.offset[1])


class TailSection(pyglet.shapes.Line):
    def __init__(self, x, y, x2, y2, width, color, batch, group, animation_manager, cumulative_dt):
        super().__init__(x, y, x2, y2, width, color, batch, group)
        self.animation_manager = animation_manager
        self.animation_manager.tail_sections.append(self)
        self.world_positions = (x, y, x2, y2)
        self.opacity_values = (0, 180, 0)
        self.opacity_times = (0.0, 0.25, 1.5)
        self.init_dt = cumulative_dt

    def update_position(self, cumulative_dt):
        # Update to viewport
        coords_1 = self.animation_manager.fit_to_viewport(self.world_positions[0], self.world_positions[1])
        coords_2 = self.animation_manager.fit_to_viewport(self.world_positions[2], self.world_positions[3])
        self.position = (coords_1[0], coords_1[1], coords_2[0], coords_2[1])

        # Update opacity
        # Return True if ready to cull from animation array
        time_passed = cumulative_dt - self.init_dt
        i_prev = 0
        for i, t in enumerate(self.opacity_times):
            if t < time_passed: i_prev = i

        if i_prev == len(self.opacity_times) - 1:
            return True
        else:
            interp_factor = (time_passed - self.opacity_times[i_prev]) / (self.opacity_times[i_prev + 1] - self.opacity_times[i_prev])
            opacity = self.opacity_values[i_prev] + (self.opacity_values[i_prev + 1] - self.opacity_values[i_prev]) * interp_factor
            self.opacity = opacity
            return False

            

        