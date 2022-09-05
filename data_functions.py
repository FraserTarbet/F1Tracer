from scipy.signal import savgol_filter

def add_animation_time(frame):
    #first_sample_time = frame["Time"].min()
    start_time = frame["LapStartTime"].iloc[0]
    frame["AnimTime"] = frame["Time"].apply(lambda x: (x - start_time)/1000000000)

    return frame


def sample_smoothing(frame):
    for axis in ("X", "Y"):
        smoothed = savgol_filter(frame[axis], 10, 3)
        frame[axis] = smoothed

    smoothed = savgol_filter(frame["Time"], 10, 3)
    frame["Time"] = smoothed

    return frame


def make_start_finish_point(frame):
    lap_start_time = frame["LapStartTime"].iloc[0]
    pre_time, pre_x, pre_y = frame[["Time", "X", "Y"]].loc[(frame["Time"] < lap_start_time)].iloc[-1]
    post_time, post_x, post_y = frame[["Time", "X", "Y"]].loc[(frame["Time"] >= lap_start_time)].iloc[0]

    interp_factor = (lap_start_time - pre_time) / (post_time - pre_time)

    finish_x = pre_x + (post_x - pre_x) * interp_factor
    finish_y = pre_y + (post_y - pre_y) * interp_factor

    finish_x, finish_y

    # travel_coefficient = (post_y - pre_y) / (post_x - pre_x)
    # travel_intercept = pre_y - travel_coefficient * pre_x

    # travel_points = []
    # for x in (finish_x - 100, finish_x + 100):
    #     y = (x * travel_coefficient) + travel_intercept
    #     travel_points.append((x, y))

    return finish_x, finish_y