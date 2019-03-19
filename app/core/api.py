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


def get_page_urls(cur_page, page_count, url):
    urls = []
    for page in range(cur_page - 3, cur_page + 3):
        if 0 < page <= page_count:
            if page != cur_page:
                urls.append({'page': page, 'url': generate_url(page, url)})
            else:
                urls.append({'page': page, 'url': None})
    return urls


def get_pagination(page, limit, url):
    pages_count = get_product_page_count(limit)
    if page > pages_count:
        raise ValueError
    navigation = {}
    if page > 1:
        navigation['left'] = generate_url(url, page - 1)
    if page < pages_count:
        navigation['right'] = generate_url(url, page + 1)
    navigation['pages'] = get_page_urls(page, pages_count, url)
    return navigation