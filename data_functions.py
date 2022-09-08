from scipy.signal import savgol_filter

def add_animation_time(frame):
    start_time = frame["LapStartTime"].iloc[0]
    frame["AnimTime"] = frame["Time"].apply(lambda x: (x - start_time)/1000000000)

    return frame


def get_tracking_window(frame):
    start_time = 0
    end_time = (frame["LapEndTime"].iloc[0] - frame["LapStartTime"].iloc[0]) / 1000000000

    return start_time, end_time


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


def add_readout_animation_times(frame):
    start_time = frame["LapStartTime"].iloc[0]
    frame["LapEndAnimTime"] = (frame["LapEndTime"] - start_time) / 1000000000
    for s in range(1, 4):
        frame[f"Sector{s}AnimTime"] = (frame[f"Sector{s}EndTime"] - start_time) / 1000000000

    return frame


def ns_to_delta_string(ns, is_benchmark=False):
    pol = "-" if ns < 0 else "+"
    ns = abs(ns)
    
    ms = ns / 1000000
    s = ms / 1000
    m = int(s / 60)
    rem_s = int(s - (m * 60))
    rem_ms = int(ms - (m * 60 + rem_s) * 1000)
    if is_benchmark == True:
        string = f"{str(m).rjust(2, '0')}:{str(rem_s).rjust(2, '0')}.{str(rem_ms)}"
    else:
        if m > 0:
            string = f"{pol}{str(m).rjust(2, '0')}:{str(rem_s).rjust(2, '0')}.{str(rem_ms).rjust(3, '0')}"
        else:
            string = f"{pol}{str(rem_s).rjust(2, '0')}.{str(rem_ms).rjust(3, '0')}"
    
    return string


def add_readout_deltas(frame):
    # Calc cumulative sector times
    frame["CumSector1Time"] = frame["Sector1Time"]
    frame["CumSector2Time"] = frame["Sector2EndTime"] - frame["LapStartTime"]
    frame["CumSector3Time"] = frame["LapTime"]

    # Identify which driver completes each sector first - these will be the benchmark times
    first_driver_per_sector = []
    for s in range(1, 4):
        first_driver = frame["Driver"].loc[frame[f"CumSector{s}Time"] == frame[f"CumSector{s}Time"].min()].iloc[0]
        first_driver_per_sector.append(first_driver)

    # Add readable delta strings
    for i, s in enumerate(range(1, 4)):
        # Cumulative time
        benchmark_time = frame[f"CumSector{s}Time"].loc[frame["Driver"] == first_driver_per_sector[i]].iloc[0]
        frame[f"CumSector{s}String"] = frame.apply(lambda x: ns_to_delta_string(
            x[f"CumSector{s}Time"] if x["Driver"] == first_driver_per_sector[i] else x[f"CumSector{s}Time"] - benchmark_time, 
            x["Driver"] == first_driver_per_sector[i]), axis=1)

        # Sector time
        benchmark_time = frame[f"Sector{s}Time"].loc[frame["Driver"] == first_driver_per_sector[i]].iloc[0]
        frame[f"Sector{s}String"] = frame.apply(lambda x: ns_to_delta_string(
            x[f"Sector{s}Time"] if x["Driver"] == first_driver_per_sector[i] else x[f"Sector{s}Time"] - benchmark_time,
            x["Driver"] == first_driver_per_sector[i]), axis=1)

    return frame