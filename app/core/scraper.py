from urllib.parse import (
    urlencode,
    urlparse
)
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from app.core.database import (
    DB,
    fill_database_by_category
)


def get_price_by_positions(url):
    items = requests.get(url).json()['positions']['primary']
    prices = []
    for item in items:
        prices.append(float(item['position_price']['amount']))
    average = round(sum(prices) / len(prices), ndigits=1)
    median = sorted(prices)[round(len(prices) / 2)]
    return average, median


def get_category_by_url(url):
    return urlparse(url).path.replace('/', '')


def get_manufacturer(url):
    return requests.get(url).json()['manufacturer']['name']


def process_product(product):
    products = DB.products
    item = products.find_one({'key': product['key']})
    if not item:
        print('not exist')
        products.insert(product, check_keys=False)
    else:
        print('exist')
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in item['price']:
            products.update_one({'key': product['key']}, {'$set': {f'price.{today}': product['price'][today],
                                                                   'current_price': product['price'][today]}})


def get_data_by_request(url, category):
    items = requests.get(url).json()['products']
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
        if data['manufacturer'] not in DB.vendors.find_one({'category': category})['vendors']:
            DB.vendors.update_one({'category': category}, {'$push': {'vendors': data['manufacturer']}})
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
    return requests.get(f'{url}/{category}?{urlencode(params)}').json()['page']['last']


def generate_urls(url, category, page_count):
    for counter in range(1, page_count + 1):
        params = {'price[from]': '1.00',
                  'page': counter}
        yield f'{url}/{category}?{urlencode(params)}'


def parse_catalog_item(url):
    html = requests.get(url).text
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


def get_categories_structure(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    base_category_names = [category.text.replace('\xa0', ' ') for category in
                           soup.find_all('span', class_='catalog-navigation-classifier__item-title-wrapper')]
    base_categories_blocks = soup.find_all('div', class_='catalog-navigation-list__category')
    base_categories = {}
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
                categories[category_name] = {}
                categories[category_name]['name'] = category_block.find(
                    'span', class_='catalog-navigation-list__dropdown-title').text.strip().replace('\xa0', ' ')
                categories[category_name]['img_url'] = category_block.find(
                    'span', class_='catalog-navigation-list__dropdown-image').get('style').split(
                        'url(//')[-1].replace(');', '')
            subcategories[subcategory_name] = categories
        base_categories[base_category_name] = subcategories


def main():
    base_url = 'https://catalog.api.onliner.by/search'
    categories = ('mobile', 'notebook')
    counter = 0
    for category in categories:
        fill_database_by_category(category)
        page_count = get_page_count(base_url, category)
        for url in generate_urls(base_url, category, page_count):
            for data in get_data_by_request(url, category):
                process_product(data)
                counter += 1
                print(counter, 'from', page_count * 30)
                if counter == 10:
                    exit()


if __name__ == '__main__':
    main()
