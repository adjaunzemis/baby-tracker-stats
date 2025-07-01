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


def main():
    DATA_FOLDER = "./data/export_20250701"
    MAX_DATE_LILY = datetime(2022, 9, 24)
    MAX_DATE_EVIE = datetime(2025, 7, 6)

    lily_diapers = read_diaper_data(folder=DATA_FOLDER, baby=BabyName.LILY, max_date=MAX_DATE_LILY)
    print("Lily Diapers:")
    for status in DiaperStatus:
        print(f"{status} = {len(lily_diapers[status])}")
    print(f"Total = {sum(len(v) for v in lily_diapers.values())}")
    
    evie_diapers = read_diaper_data(folder=DATA_FOLDER, baby=BabyName.EVIE, max_date=MAX_DATE_EVIE)
    print("Evie Diapers:")
    for status in DiaperStatus:
        print(f"{status} = {len(evie_diapers[status])}")
    print(f"Total = {sum(len(v) for v in evie_diapers.values())}")

if __name__ == "__main__":
    main()
