import math
from pymongo import MongoClient
from pprint import pprint


def create_database_connection():
    client = MongoClient()
    return client.main_database


DB = create_database_connection()


def get_products_preview(category, fields=None, page=1, limit=30):
    if fields is None:
        fields = {}
    skip = (page - 1) * limit
    return DB.products.find({'category': category,
                             **fields},
                            {'full_name': 1,
                             'description': 1,
                             'img_url': 1,
                             'current_price': 1,
                             'key': 1,
                             'category': 1,
                             '_id': 0}).skip(skip).limit(limit)


def get_product_data(product_name):
    return DB.products.find_one({'key': product_name})


def get_product_page_count(limit, filters):
    return math.ceil(DB.products.count_documents({**filters}) / limit)


def check_category(category):
    return DB.categories.find_one({'category': category})


def get_vendors_by_category(category):
    return DB.vendors.find_one({'category': category}, {'_id': 0,
                                                        'vendors': 1})['vendors']


def fill_database_by_category(category):
    if not DB.categories.find_one({'category': category}):
        DB.categories.insert_one({'category': category})

    if not DB.vendors.find_one({'category': category}):
        DB.vendors.insert_one({'category': category,
                               'vendors': []})


def parse_data(data):
    ans = {}
    for key, value in data.items():
        if isinstance(value, list):
            ans[key] = {'$in': value}
    return ans


if __name__ == '__main__':
    pprint(DB.products.find_one({}))
