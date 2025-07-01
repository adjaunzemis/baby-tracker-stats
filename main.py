import csv
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

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
    with open(file, "r", newline='') as fp:
        diapers = [DiaperData(baby=row['Baby'], time=datetime.strptime(row["Time"], TIME_FORMAT), status=row["Status"]) for row in csv.DictReader(fp)]
    
    if max_date is not None:
        diapers = [d for d in diapers if d.time < max_date]

    diapers = {status: [d for d in diapers if d.status == status] for status in DiaperStatus}

    return diapers


@dataclass(frozen=True, kw_only=True)
class SleepData:
    baby: BabyName
    time: datetime
    duration: float


def read_sleep_data(folder: str, baby: BabyName, max_date: datetime | None = None) -> list[SleepData]:
    file = f"{folder}/{baby}_sleep.csv"
    with open(file, "r", newline='') as fp:
        sleeps = [SleepData(baby=row['Baby'], time=datetime.strptime(row["Time"], TIME_FORMAT), duration=int(row["Duration (min)"].replace(",", ""))) for row in csv.DictReader(fp) if len(row["Duration (min)"]) > 0]
    
    if max_date is not None:
        sleeps = [d for d in sleeps if d.time < max_date]

    return sleeps


def main():
    DATA_FOLDER = "./data/export_20250701"
    MAX_DATES = {BabyName.LILY: datetime(2022, 9, 24), BabyName.EVIE: datetime(2025, 7, 6)}

    for baby_name in BabyName:
        print(f"{baby_name} Data:")
        diapers = read_diaper_data(folder=DATA_FOLDER, baby=baby_name, max_date=MAX_DATES[baby_name])
        print(f"\tDiapers:")
        for status in DiaperStatus:
            print(f"\t\t{status} = {len(diapers[status])}")
        print(f"\t\tTotal = {sum(len(v) for v in diapers.values())}")
        
        sleeps = read_sleep_data(folder=DATA_FOLDER, baby=baby_name, max_date=MAX_DATES[baby_name])
        print(f"\tSleeps:")
        print(f"\t\tTotal: {len(sleeps)}")
        print(f"\t\tShortest: {min(s.duration for s in sleeps)}")
        print(f"\t\tLongest: {max(s.duration for s in sleeps)}")


if __name__ == "__main__":
    main()
