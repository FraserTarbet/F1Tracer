from scipy.signal import savgol_filter

def add_animation_time(frame):
    first_sample_time = frame["Time"].min()
    frame["AnimTime"] = frame["Time"].apply(lambda x: (x - first_sample_time)/1000000000)

    return frame


def sample_smoothing(frame):
    for axis in ("X", "Y"):
        smoothed = savgol_filter(frame[axis], 10, 3)
        frame[axis] = smoothed

    smoothed = savgol_filter(frame["Time"], 10, 3)
    frame["Time"] = smoothed

    return frame