import pyglet
import data_functions
import read_database
import trace



window = pyglet.window.Window(640, 640)
batch = pyglet.graphics.Batch()
static_batch = pyglet.graphics.Batch()
animation_manager = trace.AnimationManager()

ver_frame = read_database.read_lap_samples("2022-08-27", "Qualifying", 1, 8)
ver_frame_smooth = data_functions.sample_smoothing(ver_frame.copy())
sai_frame = read_database.read_lap_samples("2022-08-27", "Qualifying", 55, 10)
sai_frame_smooth = data_functions.sample_smoothing(sai_frame.copy())

racing_line_frame = data_functions.fit_to_window(window, ver_frame, 10)
racing_line_trace = trace.RacingLine(static_batch, 5, (255, 255, 255), racing_line_frame)

colors = [
    (0, 0, 255),
    (155, 155, 155),
    (255, 0, 0),
    (255, 255, 0)
    ]
radii = [
    0,
    5,
    0,
    5
]
for i, frame in enumerate([ver_frame, ver_frame_smooth, sai_frame, sai_frame_smooth]):
    frame = data_functions.add_animation_time(frame)
    frame = data_functions.fit_to_window(window, frame, 10)
    new_trace = trace.Trace(batch, radii[i], colors[i], frame, animation_manager)


# ver_trace = trace.Trace(batch, 10, (0, 0, 255), ver_frame, animation_manager)
# ver_trace_smooth = trace.Trace(batch, 5, (255, 255, 255), ver_frame_smooth, animation_manager)



#pyglet.clock.schedule_interval(animation_manager.update_traces, 1/30)
pyglet.clock.schedule(animation_manager.update_traces)
fps_display = pyglet.window.FPSDisplay(window=window)
pyglet.options["vsync"] = False

frame = 0

@window.event
def on_draw():
    window.clear()
    static_batch.draw()
    batch.draw()
    fps_display.draw()

if __name__ == "__main__":
    pyglet.app.run()
    # print(ver_frame.head())
    # print(ver_frame_smooth.head())