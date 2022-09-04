import pyglet


class Trace(pyglet.shapes.Circle):
    def __init__(self, batch, radius, color, frame):
        #x, y = frame[["X", "Y"]].iloc[0]
        super().__init__(200, 200, radius, color=color, batch=batch)