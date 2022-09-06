import pyglet


class Heading():
    def __init__(self, window, position, height, text, font_size, font_color, bg_color, batch, GUI_groups):
        self.bg = pyglet.shapes.Rectangle(
            x=0,
            y=position,
            width=window.width,
            height=height,
            color=bg_color,
            batch=batch,
            group=GUI_groups[0]
        )
        self.text = pyglet.text.Label(
            text=text,
            font_name="TitilliumWeb-Regular",
            font_size=font_size,
            color=font_color,
            bold=False,
            x=5,
            y=position + height / 2,
            anchor_y="center",
            batch=batch,
            group=GUI_groups[1]
        )