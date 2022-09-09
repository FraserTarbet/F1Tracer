import pandas as pd
import pyglet
import animation_manager
import data_functions
import headings
import read_database
import readout
import trace
import minimap


pyglet.font.add_directory("fonts")

window = pyglet.window.Window(640, 640)
batch = pyglet.graphics.Batch()
groups = [
    "background",
    "midground",
    "foreground",
    "overlay",
    "GUI_back",
    "GUI_mid",
    "GUI_front"
]
group_dict = {}
for i, group_name in enumerate(groups):
    group_dict[group_name] = pyglet.graphics.OrderedGroup(i)

animation_manager = animation_manager.AnimationManager(window)

static_elements = []


def full_lap_follow(session_date, session_name, driver_lap_tcam_tracked_tuples, heading1, heading2, buffer_seconds, master_lap_index=0):
    raw_frames = []
    smooth_frames = []
    tracked_traces = []

    # Driver traces
    for driver, lap, tcam, tracked in driver_lap_tcam_tracked_tuples:
        # Get frames
        frame = read_database.read_lap_samples(session_date, session_name, driver, lap, buffer_seconds)
        raw_frame = frame.copy()
        raw_frame = data_functions.interpolate_gaps(raw_frame)
        raw_frame = data_functions.add_animation_time(raw_frame)
        raw_frames.append(raw_frame)

        smooth_frame = frame.copy()
        smooth_frame = data_functions.interpolate_gaps(smooth_frame)
        smooth_frame = data_functions.sample_smoothing(smooth_frame)
        smooth_frame = data_functions.add_animation_time(smooth_frame)
        smooth_frames.append(smooth_frame)

        tracking_window = data_functions.get_tracking_window(smooth_frame)

        # Make traces
        raw_trace = trace.Trace(
            batch=batch, 
            group_dict=group_dict, 
            radius=5, 
            frame=raw_frame, 
            animation_manager=animation_manager, 
            tracking_window=None, 
            tla=False, 
            tcam=tcam, 
            tail=True
        )
        smooth_trace = trace.Trace(
            batch=batch,
            group_dict=group_dict,
            radius=10,
            frame=smooth_frame,
            animation_manager=animation_manager,
            tracking_window=tracking_window,
            tla=True,
            tcam=tcam,
            tail=False
        )

        if tracked: tracked_traces.append(smooth_trace)

    animation_manager.tracked_traces = tracked_traces

    # Racing line and start/finish marker based on master lap
    trace.RollingRacingLine(
        batch=batch, 
        group_dict=group_dict, 
        width=3, 
        frame=raw_frames[master_lap_index], 
        rolling_samples=50, 
        animation_manager=animation_manager
    )
    start_finish_point = data_functions.make_start_finish_point(raw_frames[master_lap_index])
    trace.StartFinishPoint(
        world_point=start_finish_point, 
        radius=5, 
        color=(0, 0, 0), 
        batch=batch, 
        group_dict=group_dict, 
        animation_manager=animation_manager
    )

    # Minimap, headings, etc.
    minimap.Minimap((20, 20), 180, raw_frames[master_lap_index], batch, group_dict, animation_manager)

    h1 = headings.Heading(window, window.height - 40, 40, heading1, 18, (255, 255, 255, 255), (255, 30, 0), batch, group_dict)
    h2 = headings.Heading(window, window.height - 70, 30, heading2, 14, (255, 255, 255, 255), (0, 0, 0), batch, group_dict)
    for h in (h1, h2): static_elements.append(h)

    note_text = "Note: This animation contains imprecisions due to source telemetry's low sample rate (~5Hz) and significant jitter." \
        "Small markers follow an interpolated version of the raw signal. Large markers represent a smooth, heavily filtered signal."
    
    note_doc = pyglet.text.document.UnformattedDocument(note_text)
    note_doc.set_style(0, 100, attributes={
        "font_name": "TitilliumWeb-Regular",
        "font_size": 9,
        "color": (21, 21, 30, 255)
    })
    note_layout = pyglet.text.layout.TextLayout(note_doc, 350, 60, True, batch=batch, group=group_dict["GUI_front"], wrap_lines=True)
    note_layout.position = (250, 10)

    static_elements.append(note_layout)

    # Lap/sector time readouts
    readout_frames = []
    for driver, lap, tcam, tracked in driver_lap_tcam_tracked_tuples:
        readout_data = read_database.read_times(session_date, session_name, driver, lap)
        readout_data = data_functions.add_readout_animation_times(readout_data)
        readout_frames.append(readout_data)
    readout_frame = pd.concat(readout_frames)
    readout_frame.reset_index(inplace=True, drop=True)
    readout_frame = data_functions.add_readout_deltas(readout_frame)

    readout.Readout(readout_frame, (420, 540), animation_manager, batch, group_dict)




# driver_lap_tcam_tracked_tuples = [
#     (1, 8, False, True),
#     (55, 10, True, True),
#     (31, 12, True, False),
#     (44, 19, True, False),
#     (11, 8, True, True),
#     (16, 12, False, True),
#     (14, 15, False, False),
#     (63, 7, False, False)
# ]
# full_lap_follow("2022-08-27", "Qualifying", driver_lap_tcam_tracked_tuples, "Belgian Grand Prix 2022", "Qualifying Laps", 3, 0)

driver_lap_tcam_tracked_tuples = [
    (1, 11, False, True),
    (16, 17, False, True),
    (55, 17, True, True),
    (44, 14, True, True),
    (11, 18, True, False),
    (63, 14, False, False),
    (4, 17, True, False)
]
full_lap_follow("2022-09-03", "Qualifying", driver_lap_tcam_tracked_tuples, "Dutch Grand Prix 2022", "Qualifying Laps", 3, 0)


pyglet.options["vsync"] = False
pyglet.gl.glClearColor(247/255, 244/255, 241/255, 1)

pyglet.clock.schedule(animation_manager.update_traces)

@window.event
def on_draw():
    window.clear()
    batch.draw()


if __name__ == "__main__":
    animation_manager.run()
    pyglet.app.run()