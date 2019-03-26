import math
from pprint import pprint
from pymongo import MongoClient


def create_database_connection():
    client = MongoClient()
    return client.main_database


DB = create_database_connection()


def get_one_product_by_category(category):
    return DB.products.find_one({'category': category})


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
    return DB.categories.find_one({'category': category}, {'_id': 0,
                                                           'vendors': 1})['vendors']


def parse_data(data):
    ans = {}
    for category, filters in data.items():
        for key, value in filters.items():
            if category == 'single':
                if isinstance(value, list):
                    ans[key] = {'$in': value}
            elif category == 'ranges':
                if value:
                    ans[key] = {}
                    for k, v in value.items():
                        if k == 'from':
                            ans[key]['$gte'] = float(v)
                        elif k == 'to':
                            ans[key]['$lte'] = float(v)
    return ans


def get_list_categories():
    return [category['category'] for category in DB.categories.find({}, {'_id': 0,
                                                                         'category': 1})]


def get_categories_structure():
    return DB.categories_structure.find_one({}, {'_id': 0})['structure']


if __name__ == '__main__':
    pprint(list(DB.categories.find()))
