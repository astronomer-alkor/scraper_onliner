from datetime import datetime
from .celery_config import celery
from app.core.parser_helper import (
    get_manufacturer,
    get_price_by_positions,
    parse_catalog_item,
    process_product,
    get_response
)
from app.core.machine_learning import get_prediction
from app.core.database import DB


@celery.task
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
            average, median = get_price_by_positions(item['prices']['url'])
        except TypeError:
            continue
        today = datetime.now().strftime('%Y-%m-%d')
        current_price['price_average'] = average
        current_price['price_median'] = median
        current_price['price_min'] = min_price
        current_price['price_max'] = max_price
        data['current_price'] = current_price
        data['prediction_price'] = {}
        data['price'][today] = current_price
        if item['images']['header']:
            data['img_url'] = ''.join(('https:', item['images']['header']))
        else:
            data['img_url'] = ''
        data['category'] = category
        product = DB.products.find_one({'key': data['key']})
        if not product:
            data['spec'] = parse_catalog_item(data['html_url'])
        process_product(data)


@celery.task
def update_price_by_category(_, product_category):
    today = datetime.now().strftime('%Y-%m-%d')
    category = DB.categories.find_one({'category': product_category})
    if today not in category['price']:
        data = [item['current_price'] for item in DB.products.find({'category': product_category})]
        if data:
            category_price_average = round(sum([item['price_average'] for item in data]) / len(data), ndigits=1)
            category_price_median = round(sum([item['price_median'] for item in data]) / len(data), ndigits=1)
            data = {'price_average': category_price_average, 'price_median': category_price_median}
            DB.categories.update_one({'category': product_category}, {'$set': {f'price.{today}': data}})
    category = DB.categories.find_one({'category': product_category})
    if len(category['price']) > 2:
        prediction = get_prediction(category['price'])
    else:
        prediction = {}
    DB.categories.update_one({'category': product_category},
                             {'$set': {'prediction_price': prediction}})
