from scipy.signal import savgol_filter

def add_animation_time(frame):
    first_sample_time = frame["Time"].min()
    frame["AnimTime"] = frame["Time"].apply(lambda x: (x - first_sample_time)/1000000000)

    return frame


def fit_to_window(window, frame, border=0):
    min_x = frame["X"].min()
    max_x = frame["X"].max()
    min_y = frame["Y"].min()
    max_y = frame["Y"].max()

    track_width = max_x - min_x
    track_height = max_y - min_y
    longest_dimension = max(track_width, track_height)
    plot_size = min(window.height, window.width) - border * 2
    scale_factor = plot_size / longest_dimension

    frame["X_fit"] = frame["X"].apply(lambda x: ((x - min_x) * scale_factor) + border)
    frame["Y_fit"] = frame["Y"].apply(lambda y: ((y - min_y) * scale_factor) + border)

    return frame


def sample_smoothing(frame):
    for axis in ("X", "Y"):
        smoothed = savgol_filter(frame[axis], 10, 3)
        frame[axis] = smoothed

    smoothed = savgol_filter(frame["Time"], 10, 3)
    frame["Time"] = smoothed

    return frame