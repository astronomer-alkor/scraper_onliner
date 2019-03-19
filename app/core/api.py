from urllib.parse import (
    urlparse,
    urlunparse,
    urlencode
)
from app.core.database import get_product_page_count


def generate_url(url, page):
    parsed_url = list(urlparse(url))
    query = parsed_url[4]
    if not query:
        query = f'page={page}'
        parsed_url[4] = query
    else:
        queries = {}
        for query in query.split('&'):
            key, value = query.split('=')
            queries[key] = value
        queries['page'] = page
        parsed_url[4] = urlencode(queries)
    return urlunparse(parsed_url)


def get_pagination(page, limit, url):
    pages_count = get_product_page_count(limit)
    if page > pages_count:
        raise ValueError
    navigation = {}
    if page > 1:
        navigation['left'] = generate_url(url, page - 1)
    if page < pages_count:
        navigation['right'] = generate_url(url, page + 1)
    return navigation
