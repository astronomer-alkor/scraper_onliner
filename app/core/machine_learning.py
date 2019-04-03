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
    x = np.append(x, 1)
    x = np.append(x, 2)
    x = np.append(x, 3)
    y = np.append(y, 2700)
    y = np.append(y, 2750)
    y = np.append(y, 2800)
    x = np.asarray([1000, 3250, 5500, 10000, 32500, 55000, 77500, 100000, 200000])
    y = np.asarray([1100, 500, 288, 200, 113, 67, 52, 44, 5])
    fitting_parameters, covariance = curve_fit(exponential_fit, list(x), list(y))
    for _ in range(count):
        dates.append(datetime.strftime(datetime.strptime(dates[-1], '%Y-%m-%d') + timedelta(days=1), '%Y-%m-%d'))
        new_x = x[-1] + 1
        new_y = exponential_fit(new_x, *fitting_parameters)
        np.append(x, new_x)
        np.append(y, new_y)
    print(dict(zip(dates, y)))
    return dict(zip(dates, y))


def get_all_prediction(prices):
    d = defaultdict(list)
    dates = list(prices.keys())
    for item in prices.values():
        for k, v in item.items():
            d[k].append(v)
    data = {j: price_prediction(dict(zip(dates, i))) for j, i in d.items()}

    result_values = []
    for index, i in enumerate(data.values()):
        price = []
        for j in i:
            price.append(list(j.values())[index])
        result_values.append(dict(zip(data.keys(), price)))

    result = dict(zip(dates, result_values))
    return result


if __name__ == '__main__':
    from app.core.database import DB
    from pprint import pprint
    prices = DB.products.find_one({})['price']
    get_all_prediction(prices)
