from datetime import (
    datetime,
    timedelta
)
from collections import defaultdict
import numpy as np
from scipy.optimize import curve_fit


def exponential_fit(x, a, b, c):
    return a * np.exp(-b * x) + c


def price_prediction(prices, count=1):
    x = np.array([i for i in range(len(prices.keys()))])
    dates = list(prices.keys())
    y = np.array(list(prices.values()))
    fitting_parameters, covariance = curve_fit(exponential_fit, list(x), list(y))
    for _ in range(count):
        dates.append(datetime.strftime(datetime.strptime(dates[-1], '%Y-%m-%d') + timedelta(days=1), '%Y-%m-%d'))
        new_x = x[-1] + 1
        new_y = round(exponential_fit(new_x, *fitting_parameters), ndigits=2)
        x = np.append(x, new_x)
        y = np.append(y, new_y)
    return dict(zip(dates, y))


def get_all_prediction(prices):
    d = defaultdict(list)
    dates = list(prices.keys())
    for item in prices.values():
        for k, v in item.items():
            d[k].append(v)
    data = {j: price_prediction(dict(zip(dates, i))) for j, i in d.items()}
    new_dates = list(list(data.values())[0].keys())

    result_values = []
    for i in list(zip(*[list(i.values()) for i in data.values()])):
        result_values.append(dict(zip(list(data.keys()), i)))

    result = dict(zip(new_dates, result_values))
    return result


if __name__ == '__main__':
    from app.core.database import DB
    from pprint import pprint
    prices = DB.categories.find_one({'category': 'tabletpc'})['price']
    pprint(prices)
    pprint(get_all_prediction(prices))
