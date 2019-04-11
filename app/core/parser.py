from urllib.parse import (
    urlencode,
    urlparse,
    urljoin
)
from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup
from celery import chord
from app.core.database import (
    DB,
    get_list_categories,
)
from app.core.parser_helper import get_response
from app.core.tasks import (
    get_data_by_request,
    update_price_by_category
)


def get_category_by_url(url):
    return urlparse(url).path.replace('/', '')


def get_page_count(url, category):
    params = {'price[from]': '1.00',
              'page': 1}
    return get_response(f'{url}/{category}?{urlencode(params)}').json()['page']['last']


def generate_urls(url, category, page_count):
    for counter in range(1, page_count + 1):
        params = {'price[from]': '1.00',
                  'page': counter}
        yield f'{url}/{category}?{urlencode(params)}'


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
                                'vendors': [],
                                'price': {}} for category in set(category_names)])


def parse_category(category):
    base_url = 'https://catalog.api.onliner.by/search'
    page_count = get_page_count(base_url, category)
    chord(get_data_by_request.s(url, category)
          for url in generate_urls(base_url, category, page_count))(update_price_by_category.s(category))


def parse_categories(categories):
    pool = ThreadPool(3)
    categories = ('tabletpc',)
    pool.map(parse_category, categories)


def main():
    categories = get_list_categories()
    parse_categories(categories)


if __name__ == '__main__':
    main()
