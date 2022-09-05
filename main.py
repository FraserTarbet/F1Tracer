import pyglet
import animation_manager
import data_functions
import read_database
import trace



window = pyglet.window.Window(640, 640)
batch = pyglet.graphics.Batch()
background = pyglet.graphics.OrderedGroup(0)
midground = pyglet.graphics.OrderedGroup(1)
foreground = pyglet.graphics.OrderedGroup(2)
static_batch = pyglet.graphics.Batch()
animation_manager = animation_manager.AnimationManager(window)

ver_frame = read_database.read_lap_samples("2022-08-27", "Qualifying", 1, 8, 3)
ver_frame_smooth = data_functions.sample_smoothing(ver_frame.copy())
sai_frame = read_database.read_lap_samples("2022-08-27", "Qualifying", 55, 10, 3)
sai_frame_smooth = data_functions.sample_smoothing(sai_frame.copy())

racing_line_frame = data_functions.add_animation_time(ver_frame.copy())
racing_line_trace = trace.RollingRacingLine(batch, midground, 3, (21, 21, 30), racing_line_frame, 50, animation_manager)

start_finish_point = data_functions.make_start_finish_point(ver_frame.copy())
start_finish_trace = trace.StartFinishPoint(start_finish_point, 8, (0, 0, 0), batch, midground, animation_manager)

radii = [
    5,
    10,
    5,
    10
]
traces = []
for i, frame in enumerate([ver_frame, ver_frame_smooth, sai_frame, sai_frame_smooth]):
    frame = data_functions.add_animation_time(frame)
    traces.append(trace.Trace(batch, foreground, radii[i], frame, animation_manager))

animation_manager.tracked_traces = [traces[1], traces[3]]


pyglet.clock.schedule(animation_manager.update_traces)

fps_display = pyglet.window.FPSDisplay(window=window)
pyglet.options["vsync"] = False
pyglet.gl.glClearColor(247/255, 244/255, 241/255, 1)

@window.event
def on_draw():
    window.clear()
    static_batch.draw()
    batch.draw()
    fps_display.draw()


if __name__ == "__main__":
    animation_manager.run()
    pyglet.app.run()