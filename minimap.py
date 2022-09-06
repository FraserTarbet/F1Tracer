import pyglet


class Minimap():
    def __init__(self, screen_position, size, frame, batch, GUI_groups, animation_manager):
        self.animation_manager = animation_manager
        self.animation_manager.minimap = self
        self.screen_position = screen_position
        self.backdrop = pyglet.shapes.Rectangle(screen_position[0], screen_position[1], size, size,
            color=(255, 255, 255), batch=batch, group=GUI_groups[0])
        self.backdrop.opacity = 180
        
        self.lines = []
        x_tuple = tuple(frame["X"])
        y_tuple = tuple(frame["Y"])
        self.min_x = min(x_tuple)
        self.min_y = min(y_tuple)
        max_x = max(x_tuple)
        max_y = max(y_tuple)
        max_dim = max((max_x - self.min_x), (max_y - self.min_y))
        self.scale_factor = size / (max_dim * 1.1)
        self.offset_x = (size - ((max_x - self.min_x) * self.scale_factor)) / 2
        self.offset_y = (size - ((max_y - self.min_y) * self.scale_factor)) / 2
        for i in range(len(x_tuple) - 1):
            line = pyglet.shapes.Line(
                x=((x_tuple[i] - self.min_x) * self.scale_factor) + screen_position[0] + self.offset_x, 
                y=((y_tuple[i] - self.min_y) * self.scale_factor) + screen_position[1] + self.offset_y,
                x2=((x_tuple[i+1] - self.min_x) * self.scale_factor) + screen_position[0] + self.offset_x,             
                y2=((y_tuple[i+1] - self.min_y) * self.scale_factor) + screen_position[1] + self.offset_y,
                width=3,
                color=(0, 0, 0),
                batch=batch,
                group=GUI_groups[1]
            )
            self.lines.append(line)

        self.marker = pyglet.shapes.Circle(0, 0, 5, color=(255, 30, 0), batch=batch, group=GUI_groups[2])

    def update_screen_position(self):
        world_point = self.animation_manager.view_centre
        x = ((world_point[0] - self.min_x) * self.scale_factor) + self.screen_position[0] + self.offset_x
        y = ((world_point[1] - self.min_y) * self.scale_factor) + self.screen_position[1] + self.offset_y
        self.marker.position = (x, y)