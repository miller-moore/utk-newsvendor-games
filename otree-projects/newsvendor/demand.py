from pathlib import Path

app_directory = Path(__file__).resolve().parent  # ./newsvendor/
demand_distributions_csv = app_directory / "static" / "demand_distributions.csv"
if not demand_distributions_csv.exists():
    import numpy as np
    import pandas as pd

    mu, sigma1, sigma2 = 500, 50, 100
    # np.random.lognormal
    dist1 = np.random.normal(loc=mu, scale=sigma1, size=(int(1e4),))
    dist2 = np.random.normal(loc=mu, scale=sigma2, size=(int(1e4),))
    df = pd.DataFrame({"d1": dist1, "d2": dist2})
    df.to_csv(demand_distributions_csv, header=True, index=False)
