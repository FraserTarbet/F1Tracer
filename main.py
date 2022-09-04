import pyglet
import read_database
import trace


def add_animation_time(frame):
    first_sample_time = frame["Time"].min()
    frame["AnimTime"] = frame["Time"].apply(lambda x: (x - first_sample_time)/1000000000)

    return frame


def fit_to_window(window, frame, border=0):
    min_x = frame["X"].min()
    max_x = frame["X"].max()
    min_y = frame["Y"].min()
    max_y = frame["Y"].max()

window = pyglet.window.Window()

batch = pyglet.graphics.Batch()

ver_frame = read_database.read_lap_samples("2022-08-27", "Qualifying", 1, 8)
ver_trace = trace.Trace(batch, 10, (0, 0, 255), ver_frame)



@window.event
def on_draw():
    window.clear()
    batch.draw()


if __name__ == "__main__":
    pyglet.app.run()