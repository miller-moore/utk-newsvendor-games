from pathlib import Path

import numpy as np
import pandas as pd
from rich import print

from .constants import STATIC_DIR, Constants


def get_demand_data_csv_path(as_static_url: bool, participantid: str) -> str:
    assert type(local) is bool, f"local must be boolean - got {type(local)}"
    if as_static_url:
        return f"{Constants.static_path}/demand_data_{participantid}.csv"
    return str(STATIC_DIR / f"demand_data_{participantid}.csv")


def maybe_write_demand_data_csv(data: np.ndarray, participantid: str) -> None:
    local_path = Path(get_demand_data_csv_path(as_static_url=False, participantid=participantid))
    if local_path.exists():
        print(f"""Warning: demand csv data already exists for participant {participantid}""")
    df = pd.DataFrame({"data": data})
    df.to_csv(static_path, header=True, index=False)
