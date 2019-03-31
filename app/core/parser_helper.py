from datetime import datetime
import requests
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import (
    ConnectTimeout,
    ProxyError,
    ReadTimeout,
    ConnectionError
)
from bs4 import BeautifulSoup
from proxyscrape import create_collector
from app.core.database import DB


COLLECTOR = create_collector('collector', 'https')


def manage_proxies(func):
    proxies = []

    def wrapper(*args, **kwargs):
        nonlocal proxies
        response, new_proxies = func(*args, proxies, **kwargs)
        proxies = new_proxies
        return response
    return wrapper


@manage_proxies
def get_response_use_proxy(url, proxies):
    while True:
        if proxies:
            for proxy in proxies:
                try:
                    response = requests.get(url, proxies={**proxy}, timeout=1)
                    if response.status_code == 200:
                        return response, proxies
                except (ReadTimeout, ConnectTimeout, ProxyError, ReadTimeoutError, ConnectionError):
                    continue
            proxies.clear()
        proxy = COLLECTOR.get_proxy()
        proxy = {proxy.type: ':'.join((proxy.host, proxy.port))}
        try:
            response = requests.get(url, proxies={**proxy}, timeout=1)
        except (ReadTimeout, ConnectTimeout, ProxyError, ReadTimeoutError, ConnectionError):
            continue
        if response.status_code == 200:
            proxies.append(proxy)
            return response, proxies


def get_response(url, use_proxy=True):
    if use_proxy:
        return get_response_use_proxy(url)
    return requests.get(url)


def get_manufacturer(url):
    return get_response(url).json()['manufacturer']['name']


def get_price_by_positions(url):
    items = get_response(url).json()['positions']['primary']
    prices = []
    for item in items:
        prices.append(float(item['position_price']['amount']))
    average = round(sum(prices) / len(prices), ndigits=1)
    median = sorted(prices)[round(len(prices) / 2)]
    return average, median


def parse_catalog_item(url):
    html = get_response(url).text
    soup = BeautifulSoup(html, 'lxml')
    spec_tables = soup.find('table', class_='product-specs__table').find_all('tbody', recursive=False)
    data = {}
    for spec_table in spec_tables:
        rows = spec_table.find_all('tr')
        table_header = rows[0].find('div').text.strip()
        table_data = {}
        for row in rows[1:]:
            row_items = row.find_all('td', recursive=False)
            key = row_items[0].contents[0].strip()
            try:
                value = '\n'.join([row_item.replace('\xa0', ' ') for row_item
                                   in row_items[1].find('span', class_='value__text').contents
                                   if isinstance(row_item, str)])
            except AttributeError:
                value = row_items[1].find('span')
                if value['class'] == ['i-tip']:
                    value = True
                else:
                    value = False
            except IndexError:
                continue
            if key == 'Дата выхода на рынок':
                value = int(value.replace(' г.', ''))
            table_data[key] = value
        data[table_header] = table_data
    return data


def process_product(product):
    products = DB.products
    item = products.find_one({'key': product['key']})
    if not item:
        products.insert(product, check_keys=False)
    else:
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in item['price']:
            products.update_one({'key': product['key']}, {'$set': {f'price.{today}': product['price'][today],
                                                                   'current_price': product['price'][today]}})
