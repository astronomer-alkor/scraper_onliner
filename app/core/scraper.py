from urllib.parse import (
    urlencode,
    urlparse,
    urljoin
)
from datetime import datetime
from pprint import pprint
from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup
from proxyscrape import create_collector
import requests
from requests.exceptions import (
    ConnectTimeout,
    ProxyError
)
from app.core.database import (
    DB,
    get_list_categories,
)

COLLECTOR = create_collector('collector', 'https')


def get_response(url, proxies=[]):
    while True:
        if proxies:
            if len(proxies) > 20:
                proxies.pop(0)
            for proxy in proxies:
                try:
                    response = requests.get(url, proxies={**proxy}, timeout=2)
                    if response.status_code == 200:
                        return response
                except (ConnectTimeout, ProxyError):
                    continue
            else:
                proxies.clear()
        proxy = COLLECTOR.get_proxy()
        proxy = {proxy.type: ':'.join((proxy.host, proxy.port))}
        try:
            response = requests.get(url, proxies={**proxy}, timeout=2)
        except (ConnectTimeout, ProxyError):
            continue
        if response.status_code == 200:
            proxies.append(proxy)
            return response


def get_price_by_positions(url):
    items = get_response(url).json()['positions']['primary']
    prices = []
    for item in items:
        prices.append(float(item['position_price']['amount']))
    average = round(sum(prices) / len(prices), ndigits=1)
    median = sorted(prices)[round(len(prices) / 2)]
    return average, median


def get_category_by_url(url):
    return urlparse(url).path.replace('/', '')


def get_manufacturer(url):
    return get_response(url).json()['manufacturer']['name']


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


def get_data_by_request(url, category):
    items = get_response(url).json()['products']
    for item in items:
        data = {}
        current_price = {}
        data['price'] = {}
        keys = ('id', 'key', 'full_name', 'description', 'micro_description', 'html_url')
        for key in keys:
            if isinstance(item[key], str):
                data[key] = item[key].replace('&quot;', '"')
            else:
                data[key] = item[key]
        data['manufacturer'] = get_manufacturer(item['url'])
        if data['manufacturer'] not in DB.categories.find_one({'category': category})['vendors']:
            DB.categories.update_one({'category': category}, {'$push': {'vendors': data['manufacturer']}})
        try:
            min_price = float(item['prices']['price_min']['amount'])
            max_price = float(item['prices']['price_max']['amount'])
        except TypeError:
            continue
        today = datetime.now().strftime('%Y-%m-%d')
        average, median = get_price_by_positions(item['prices']['url'])
        current_price['price_average'] = average
        current_price['price_median'] = median
        current_price['price_min'] = min_price
        current_price['price_max'] = max_price
        data['current_price'] = current_price
        data['price'][today] = current_price
        data['img_url'] = ''.join(('https:', item['images']['header']))
        data['category'] = category
        if not DB.products.find_one({'key': data['key']}):
            data['spec'] = parse_catalog_item(data['html_url'])
        yield data


def get_page_count(url, category):
    params = {'price[from]': '1.00',
              'page': 1}
    return get_response(f'{url}/{category}?{urlencode(params)}').json()['page']['last']


def generate_urls(url, category, page_count):
    for counter in range(1, page_count + 1):
        params = {'price[from]': '1.00',
                  'page': counter}
        yield f'{url}/{category}?{urlencode(params)}'


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
            table_data[key] = value
        data[table_header] = table_data
    return data


def get_categories_structure(url='https://catalog.onliner.by/'):
    html = get_response(url).text
    soup = BeautifulSoup(html, 'lxml')
    base_category_names = [category.text.replace('\xa0', ' ') for category in
                           soup.find_all('span', class_='catalog-navigation-classifier__item-title-wrapper')]
    base_categories_blocks = soup.find_all('div', class_='catalog-navigation-list__category')
    base_categories = {}
    category_names = []
    for base_category_name, base_category_block in zip(base_category_names, base_categories_blocks):
        subcategories = {}
        subcategory_blocks = base_category_block.find_all('div', class_='catalog-navigation-list__aside-item')
        for subcategory_block in subcategory_blocks:
            subcategory_name = subcategory_block.find('div', class_='catalog-navigation-list__aside-title').\
                text.strip().replace('\xa0', ' ')
            category_blocks = subcategory_block.find_all('a', class_='catalog-navigation-list__dropdown-item')
            categories = {}
            for category_block in category_blocks:
                category_name = get_category_by_url(category_block.get('href'))
                category_names.append(category_name)
                categories[category_name] = {}
                categories[category_name]['name'] = category_block.find(
                    'span', class_='catalog-navigation-list__dropdown-title').text.strip().replace('\xa0', ' ')
                categories[category_name]['img_url'] = ''.join(('https:', category_block.find(
                    'span', class_='catalog-navigation-list__dropdown-image').get('style').split(
                        'url(')[-1].replace(');', '')))
                categories[category_name]['url'] = urljoin('/categories/', category_name)
            subcategories[subcategory_name] = categories
        base_categories[base_category_name] = subcategories
    DB.categories_structure.insert_one({'structure': base_categories})
    DB.categories.insert_many([{'category': category,
                                'vendors': []} for category in category_names])


def parse_category(category):
    base_url = 'https://catalog.api.onliner.by/search'
    counter = 0
    page_count = get_page_count(base_url, category)
    for url in generate_urls(base_url, category, page_count):
        for data in get_data_by_request(url, category):
            process_product(data)
            counter += 1
            print(category, counter, 'from', page_count * 30)


def parse_categories(categories):
    pool = ThreadPool(20)
    pool.map(parse_category, categories)


def main():
    categories = get_list_categories()
    parse_categories(categories)


if __name__ == '__main__':
    main()
    # get_response('https://catalog.onliner.by/')