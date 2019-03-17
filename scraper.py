from urllib.parse import urlencode
from datetime import datetime
from app.core.database import db
from bs4 import BeautifulSoup
import requests


def process_product(product):
    products = db.products
    item = products.find_one({'key': product['key']})
    if not item:
        products.insert_one(product)
    else:
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in item['price']:
            products.update_one({'key': product['key']}, {'$set': {f'price.{today}': product['price'][today]}})


def get_data_by_request(url, category):
    items = requests.get(url).json()['products']
    for item in items:
        data = {}
        current_price = {}
        data['price'] = {}
        keys = ('id', 'key', 'name', 'description', 'micro_description', 'html_url')
        for key in keys:
            if isinstance(item[key], str):
                data[key] = item[key].replace('&quot;', '"')
            else:
                data[key] = item[key]
        current_price['price_min'] = item['prices']['price_min']['amount']
        current_price['price_max'] = item['prices']['price_max']['amount']
        data['price'][datetime.now().strftime('%Y-%m-%d')] = current_price
        data['img_url'] = ''.join(('https:', item['images']['header']))
        data['category'] = category
        data['spec'] = parse_catalog_item(data['html_url'])
        yield data


def get_page_count(url, category):
    return requests.get(f'{url}/{category}?page=1').json()['page']['last']


def generate_urls(url, category, page_count):
    for counter in range(1, page_count + 1):
        page = {'page': counter}
        yield f'{url}/{category}?{urlencode(page)}'


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
                value = '\n'.join([row_item for row_item in row_items[1].find('span', class_='value__text').contents
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


def main():
    base_url = 'https://catalog.api.onliner.by/search'
    categories = ('mobile', )
    counter = 0
    for category in categories:
        page_count = get_page_count(base_url, category)
        for url in generate_urls(base_url, category, page_count):
            for data in get_data_by_request(url, category):
                process_product(data)
                counter += 1
                print(counter)
                if counter == 20:
                    exit()


if __name__ == '__main__':
    main()
