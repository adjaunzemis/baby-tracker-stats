import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

import numpy as np
import matplotlib.pyplot as plt


TIME_FORMAT = "%m/%d/%y %I:%M %p"

class BabyName(StrEnum):
    LILY = "Lily"
    EVIE = "Evie"


class DiaperStatus(StrEnum):
    WET = "Wet"
    DIRTY = "Dirty"
    MIXED = "Mixed"
    DRY = "Dry"


@dataclass(frozen=True, kw_only=True)
class DiaperData:
    baby: BabyName
    time: datetime
    status: DiaperStatus


def read_diaper_data(folder: str, baby: BabyName, max_date: datetime | None = None) -> dict[DiaperStatus, list[DiaperData]]:
    file = f"{folder}/{baby}_diaper.csv"
    with open(file, "r", newline="") as fp:
        diapers = [DiaperData(baby=row["Baby"], time=datetime.strptime(row["Time"], TIME_FORMAT), status=row["Status"]) for row in csv.DictReader(fp)]
    
    if max_date is not None:
        diapers = [d for d in diapers if d.time < max_date]

    diapers = {status: [d for d in diapers if d.status == status] for status in DiaperStatus}

    return diapers


@dataclass(frozen=True, kw_only=True)
class SleepData:
    baby: BabyName
    time: datetime
    duration: int


def read_sleep_data(folder: str, baby: BabyName, max_date: datetime | None = None) -> list[SleepData]:
    file = f"{folder}/{baby}_sleep.csv"
    with open(file, "r", newline="") as fp:
        sleeps = [SleepData(
            baby=row["Baby"],
            time=datetime.strptime(row["Time"], TIME_FORMAT),
            duration=int(row["Duration (min)"].replace(",", ""))
        ) for row in csv.DictReader(fp) if len(row["Duration (min)"]) > 0]
    
    if max_date is not None:
        sleeps = [d for d in sleeps if d.time < max_date]

    return sleeps


class NursingSide(StrEnum):
    LEFT = "Left"
    RIGHT = "Right"


@dataclass(frozen=True, kw_only=True)
class NursingData:
    baby: BabyName
    time: datetime
    start_side: NursingSide
    left_duration: int
    right_duration: int
    total_duration: int

    

def read_nursing_data(folder: str, baby: BabyName, max_date: datetime | None = None) -> list[NursingData]:
    file = f"{folder}/{baby}_nursing.csv"
    with open(file, "r", newline="") as fp:
        nursings = [NursingData(
            baby=row["Baby"],
            time=datetime.strptime(row["Time"], TIME_FORMAT),
            start_side=row["Start side"],
            left_duration=int(row["Left duration (min)"]) if len(row["Left duration (min)"]) > 0 else 0,
            right_duration=int(row["Right Duration (min)"]) if len(row["Right Duration (min)"]) > 0 else 0,
            total_duration=int(row["Total (min)"]),
        ) for row in csv.DictReader(fp) if len(row["Total (min)"]) > 0]
    
    if max_date is not None:
        nursings = [d for d in nursings if d.time < max_date]

    return nursings


def plot_sleep_data(sleeps: list[SleepData], min_date: datetime, max_date: datetime):
    LINEWIDTH = 0.5

    COLOR_AWAKE = "#d1c580"
    COLOR_ASLEEP = "#264794"

    R_MIN = 0.2
    R_MAX = 1.0
    NUM_SAMPLES = 100
    MINUTES_PER_DAY = 24 * 60

    _, ax = plt.subplots(subplot_kw={'projection': 'polar'})

    min_timestamp = min_date.timestamp()
    max_timestamp = max_date.timestamp()
        
    # Add awake segments
    for i, sleep in enumerate(sleeps):
        if i + 1 >= len(sleeps):
            continue

        next_sleep = sleeps[i + 1]

        awake_start = sleep.time + timedelta(minutes=sleep.duration)
        awake_stop = next_sleep.time

        th_start = (awake_start.hour * 60 + awake_start.minute) * (2 * np.pi) / MINUTES_PER_DAY
        th_stop = (awake_stop.hour * 60 + awake_stop.minute) * (2 * np.pi) / MINUTES_PER_DAY
        if awake_stop.date() > awake_start.date():
            th_stop += 2 * np.pi

        r_start = R_MIN + (R_MAX - R_MIN) * (awake_start.timestamp() - min_timestamp) / (max_timestamp - min_timestamp)
        r_stop = R_MIN + (R_MAX - R_MIN) * (awake_stop.timestamp() - min_timestamp) / (max_timestamp - min_timestamp)
        
        ths = np.linspace(th_start, th_stop, NUM_SAMPLES)
        rs = np.linspace(r_start, r_stop, NUM_SAMPLES)
        plt.polar(ths, rs, lw=LINEWIDTH, color=COLOR_AWAKE)

    # Add sleep segments
    for i, sleep in enumerate(sleeps):
        sleep_start = sleep.time
        sleep_stop = sleep.time + timedelta(minutes=sleep.duration)

        th_start = (sleep_start.hour * 60 + sleep_start.minute) * (2 * np.pi) / MINUTES_PER_DAY
        th_stop = (sleep_stop.hour * 60 + sleep_stop.minute) * (2 * np.pi) / MINUTES_PER_DAY
        if sleep_stop.date() > sleep_start.date():
            th_stop += 2 * np.pi

        r_start = R_MIN + (R_MAX - R_MIN) * (sleep_start.timestamp() - min_timestamp) / (max_timestamp - min_timestamp)
        r_stop = R_MIN + (R_MAX - R_MIN) * (sleep_stop.timestamp() - min_timestamp) / (max_timestamp - min_timestamp)
        
        ths = np.linspace(th_start, th_stop, NUM_SAMPLES)
        rs = np.linspace(r_start, r_stop, NUM_SAMPLES)
        plt.polar(ths, rs, lw=LINEWIDTH, color=COLOR_ASLEEP)

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rmin(0.0)
    ax.set_rticks([])
    ax.set_xticks([])
    ax.tick_params('x', pad=2)
    ax.grid(False)
    ax.set_axis_off()


def main():
    DATA_FOLDER = "./data/export_20250701"
    MIN_DATES = {BabyName.LILY: datetime(2021, 9, 23), BabyName.EVIE: datetime(2024, 7, 5)}
    MAX_DATES = {BabyName.LILY: datetime(2022, 9, 24), BabyName.EVIE: datetime(2025, 7, 6)}

    # Diaper data
    for baby_name in BabyName:
        diapers = read_diaper_data(folder=DATA_FOLDER, baby=baby_name, max_date=MAX_DATES[baby_name])
        print(f"{baby_name} Diapers:")
        for status in DiaperStatus:
            print(f"\t{status} = {len(diapers[status])}")
        print(f"\tTotal = {sum(len(v) for v in diapers.values())}")

    # Sleep data
    for baby_name in BabyName:
        sleeps = read_sleep_data(folder=DATA_FOLDER, baby=baby_name, max_date=MAX_DATES[baby_name])
        print(f"{baby_name} Sleeps:")
        print(f"\tCount: {len(sleeps)}")
        print(f"\tTotal: {sum(s.duration for s in sleeps)} minutes, or {sum(s.duration for s in sleeps) / (24*60):.1f} days")
        print(f"\tShortest: {min(s.duration for s in sleeps)} minutes")
        print(f"\tLongest: {max(s.duration for s in sleeps)} minutes")
        
        plot_sleep_data(sleeps=sleeps, min_date=MIN_DATES[baby_name], max_date=MAX_DATES[baby_name])

    # Nursing data
    for baby_name in BabyName:
        nursings = read_nursing_data(folder=DATA_FOLDER, baby=baby_name, max_date=MAX_DATES[baby_name])
        print(f"{baby_name} Nursings:")
        print(f"\tCount: {len(nursings)}")
        print(f"\tTotal: {sum(n.total_duration for n in nursings)} minutes, or {sum(n.total_duration for n in nursings) / (24 * 60):.1f} days")
        print(f"\tShortest: {min(n.total_duration for n in nursings)} minutes")
        print(f"\tLongest: {max(n.total_duration for n in nursings)} minutes")

        nursings_left = [n for n in nursings if n.left_duration > 0]
        print(f"\tLeft Count: {len(nursings_left)}")
        print(f"\tLeft Total: {sum(n.left_duration for n in nursings_left)} minutes, or {sum(n.left_duration for n in nursings_left) / (24 * 60):.1f} days")
        print(f"\tLeft Shortest: {min(n.left_duration for n in nursings_left)} minutes")
        print(f"\tLeft Longest: {max(n.left_duration for n in nursings_left)} minutes")
        
        nursings_right = [n for n in nursings if n.right_duration > 0]
        print(f"\tRight Count: {len(nursings_right)}")
        print(f"\tRight Total: {sum(n.right_duration for n in nursings_right)} minutes, or {sum(n.right_duration for n in nursings_right) / (24 * 60):.1f} days")
        print(f"\tRight Shortest: {min(n.right_duration for n in nursings_right)} minutes")
        print(f"\tRight Longest: {max(n.right_duration for n in nursings_right)} minutes")

        print(f"\tBoth Count: {len([n for n in nursings if n.left_duration > 0 and n.right_duration > 0])}")

    plt.show()


if __name__ == "__main__":
    main()
