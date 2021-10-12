import json
import time
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any, List, Optional, Set, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from otree.api import BasePlayer, Currency, currency_range
from pydantic import BaseConfig, BaseModel
from scipy import stats


def compute_profit(player: Any) -> float:
    """Compute & return the planner's profit at the end of each game (single playthrough).

    Parameters
    ----------
    player: BasePlayer
        The player

    ## Important attributes
    retail_cost : float
        Rc - get from low/high variance options
    wholesale_cost : float
        Wc - get from low/high variance options
    holding_cost : float
        Hc - get from low/high variance options
    excess_quantity : float
        Eq - get from player cache
    order_quantity : float
        Oq - get from player's input each round
    demand_quantity : float
        Dq - draw dynamically from distribution

    # Pseudo-code:
    if sq + oq > dq:
        # we still have an excess
        rev = Dq * Rc
        sq = sq + oq - dq
        costs = oq * Wc + sq * Hc
        return rev - costs
    else:
        rev = ( sq + oq ) * Rc
        costs = oq * Wc
        return rev - costs

    Returns
    -------
    float
        Profit amount
    """

    from .models import Costs

    # get from player treatment group & map to values defined in above dictionaries
    Rc, Wc, Hc = Costs.tuple()

    # NOTE: get excess_stock from participant's cache (round_i - 1)
    Eq_1 = player.cache.get("excess_stock")
    # Oq: get from page input
    Oq = None
    # Dq: draw from the lognorm
    Dq = None

    # update the player's excess_stock for next round
    player.cache["excess_stock"] = Eq_1 + Oq - Dq

    if Eq_1 + Oq > Dq:
        return Dq * Rc - Oq * Wc - player.cache["excess_stock"] * Hc
    return (Eq_1 + Oq) * Rc - Oq * Wc


def get_demand_data_csv_path(as_asset_url: bool, participantid: str) -> str:
    from .models import STATIC_DIR, Constants

    assert type(as_asset_url) is bool, f"local must be boolean - got {type(as_asset_url)}"
    file_name = f"demand_data_{participantid}.csv"
    if as_asset_url:
        return str(Path(Constants.url_prefix) / file_name)
    return str(STATIC_DIR / file_name)


def maybe_write_demand_data_csv(data: np.ndarray, participantid: str) -> None:
    local_path = Path(get_demand_data_csv_path(as_static_url=False, participantid=participantid))
    if local_path.exists():
        print(f"""[yellow]WARNING[/]: demand csv data already exists for participant with id: {participantid}""")
    df = pd.DataFrame({"data": data})
    df.to_csv(local_path, header=True, index=False)


def get_settings() -> ModuleType:
    """Dynamically imports and return the ``otree.settings`` module.

    Before returning the settings module, a new function ``asdict`` is assigned to the module.
    This function transforms the settings module into a dictionary of setting values by name,
    and is added to the module so that ``get_settings`` can be used anywhere in the codebase
    whenever either a dictionary of dynamically imported server settings is needed. ``asdict``
    returns a dictionary that does not contain every object belonging to the module - only
    objects considered to be a server setting.

    Returns:
        ``otree.settings``: [ModuleType]
    """

    def asdict():
        from string import ascii_uppercase

        from otree import settings as settings_module

        # transform the module to a dictionary, attempting to include only setting objects
        settings_dict = {}
        for name, value in settings_module.__dict__.items():
            if name.startswith("_"):
                # don't include: private methods, private attributes, ModuleType dunder methods, etc are not settings
                continue

            # for conservatism, include the object if it's name obeys the naming convention rules for system environment variables
            allowed_chars = set("_" + ascii_uppercase)
            name_chars = set(name)
            if name_chars.issubset(allowed_chars):
                settings_dict.update({name: value})

        return settings_dict

    from otree import settings as settings_module

    if not hasattr(settings_module, "asdict"):
        setattr(settings_module, "asdict", asdict)

    return settings_module


def json_dump_settings(**kwargs) -> str:
    return json.dumps(get_settings().asdict(), **kwargs)


def apply_distribution_disruption(player: BasePlayer):
    # player distribution is generated at beginning of each playthrough & cached to the player
    # it is regenerated between the two playthroughs
    # 1st playthrough: if disruption is True in the player's treatment group, apply the disruption in round int(1/4 * playthrough_rounds) (6th when 24 rounds)
    # 2nd playthrough: all participants have a disruption in round int(3/4 * playthrough_rounds) (18th when 24 rounds)
    pass


def lognormalize_normal_samples(normal_rvs: np.ndarray) -> np.ndarray:
    """Fit a lognormal distribution to normally distributed random variables and return
    lognormal random variables sampled from the fitted lognormal distribution.

    Ex:
        normal_rvs = np.random.normal(500, 100, size=size)
        plt.hist(normal_rvs, bins=50)
        plt.show()

        lognormal_rvs = lognormalize_normal_samples(normal_rvs)
        plt.hist(lognormal_rvs, bins=50)
        plt.show()

    Ex:
        lognormal_rvs_low = np.random.lognormal(6.212, 0.067, size=int(1e4)) # low
        lognormal_rvs_high = np.random.lognormal(6.15, 0.35, size=int(1e4)) # high

        plt.hist(lognormal_rvs_low, bins=200, density=True)
        plt.xlim(0, 1000)
        plt.show()

        plt.hist(lognormal_rvs_high, bins=200, density=True)
        plt.xlim(0, 1000)
        plt.show()

    """

    size = len(normal_rvs)

    # lognormal "scale" parameter: set to the mean of the underlying normal random variables
    fscale = normal_rvs.mean()

    # lognormal "loc" parameter: if the sample minimum is negative, set to some value shifted right by the amount equal to abs(sample minimum), else set to 0
    floc = 0 - min(0, normal_rvs.min())

    # fit the lognormal distribution to normal random variables (using the floc & fscale found above)
    # to get the parameters of the lognormal dist from which a continuous dist will be made for drawing new samples
    s, loc, scale = stats.lognorm.fit(normal_rvs, floc=floc, fscale=fscale)
    fitted_lognorm_distribution = stats.lognorm(s=s, loc=loc, scale=scale)  # fitted

    # get len(normal_rvs) random samples from the fitted lognormal distribution
    lognormal_rvs = fitted_lognorm_distribution.rvs(size)

    # Example of how to generate with numpy from here even though it's overkill here because scipy must be used anyhow to get the "scale" & "s" parameters - see the above scipy call to fit the lognormal dist:
    # # Note: for explanation of the next line of code, see https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html
    # lognorm_mu, lognorm_sig = np.log(scale), s  ## FYI: this transformation is needed when generating from numpy, i.e., via `np.random.lognormal`
    # lognormal_rvs_numpy = np.random.lognormal(lognorm_mu, lognorm_sig, size=size)

    ## Debug prints to show how close the distr's are
    ## print("scipy lognormal samples; mean=%s, std=%s" % (lognormal_rvs.mean(), lognormal_rvs.std()))
    ## print("numpy lognormal samples; mean=%s, std=%s" % (lognormal_rvs_numpy.mean(), lognormal_rvs_numpy.std()))

    # return the lognormalized random samples
    return lognormal_rvs


def normalize_lognormal_samples(lognormal_rvs: np.ndarray) -> np.ndarray:
    """[summary]

    [extended_summary]

    Parameters
    ----------
    lognormal_rvs : np.ndarray
        [description]

    Returns
    -------
    np.ndarray
        [description]

    # Example:
        data = normalize_lognormal_samples(lognormal_rvs_high)
        plt.hist(data, bins=50, density=True)
        norm = stats.norm(data.mean(), data.std())
        x = np.linspace(min(data), max(data),len(data))
        plt.plot(x, norm.pdf(x), linewidth=2, color='r')
        plt.show()
    """
    mu, sig = stats.norm.fit(lognormal_rvs)
    norm = stats.norm(mu, sig)
    return norm.rvs(len(lognormal_rvs))


def get_time(iso: bool = False) -> float:
    t = datetime.utcnow()
    if not iso:
        return t.timestamp()
    return t.isoformat()


def reorderLegend(ax=None, order=None, key=None, unique=False, **legend_kwargs):
    """Returns tuple of handles, labels for axis ax, after reordering them to conform to the label order `order`, and if unique is True, after removing entries with duplicate labels."""

    if ax is None:
        ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()

    # sort both labels and handles by labels
    labels, handles = list(zip(*sorted(zip(labels, handles), key=lambda t: t[0])))

    if order is not None:
        # Sort according to a given list (not necessarily complete)
        keys = dict(list(zip(order, list(range(len(order))))))
        labels, handles = list(zip(*sorted(zip(labels, handles), key=lambda t, keys=keys: keys.get(t[0], np.inf))))

    if unique:
        # Keep only the first of each handle
        # from  more_itertools import unique_everseen   # Use this instead??
        labels, handles = list(zip(*unique_everseen(list(zip(labels, handles)), key=key or labels)))

    ax.legend(handles, labels, **legend_kwargs)
    return handles, labels


def unique_everseen(seq: Union[list, tuple, set, range, zip], key=None):
    check_type = lambda o: isinstance(o, (list, tuple, set, range, zip))
    assert check_type(seq), f"seq must be a list, tuple, set, range, or zip - got {type(seq)}"
    seen = set()
    seen_add = seen.add
    if not key:
        key = seq
    elif not check_type(key):
        key = [key]
    key = list(key)
    return [x for x, k in zip(seq, key) if not (k in seen or seen_add(k))]
