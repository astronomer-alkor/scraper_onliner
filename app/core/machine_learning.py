from datetime import (
    datetime,
    timedelta
)
from collections import defaultdict
import numpy as np
from scipy.interpolate import (
    splrep, splev
)


def make_prediction(prices, count=2):
    x = np.array([i for i in range(len(prices.keys()))])
    dates = list(prices.keys())
    y = np.array(list(prices.values()))
    f = splrep(list(x), list(y), k=1, s=0)
    for _ in range(count):
        dates.append(datetime.strftime(datetime.strptime(dates[-1], '%Y-%m-%d') + timedelta(days=1), '%Y-%m-%d'))
        new_x = x[-1] + 1
        new_y = round(float(splev(new_x, f)), ndigits=2)
        x = np.append(x, new_x)
        y = np.append(y, new_y)
    return dict(zip(dates[len(dates) - count:], y[len(dates) - count:]))


def get_prediction(prices):
    d = defaultdict(list)
    dates = list(prices.keys())
    for item in prices.values():
        for k, v in item.items():
            d[k].append(v)
    data = {j: make_prediction(dict(zip(dates, i))) for j, i in d.items()}
    new_dates = list(list(data.values())[0].keys())

    result_values = []
    for i in list(zip(*[list(i.values()) for i in data.values()])):
        result_values.append(dict(zip(list(data.keys()), i)))

    result = dict(zip(new_dates, result_values))
    return result
