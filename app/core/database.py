import math
from pymongo import MongoClient
from pprint import pprint


def create_database_connection():
    client = MongoClient()
    return client.main_database


DB = create_database_connection()


def get_products_preview(page=1, limit=30):
    skip = (page - 1) * limit
    return DB.products.find({}, {'full_name': 1,
                                 'description': 1,
                                 'img_url': 1,
                                 'current_price': 1,
                                 'key': 1,
                                 'category': 1,
                                 '_id': 0}).skip(skip).limit(limit)


def get_product_data(product_name):
    return DB.products.find_one({'key': product_name})


def get_product_page_count(limit):
    return math.ceil(DB.products.count_documents({}) / limit)


# def get_vendors(category):
#     vendors = DB.products.find({'category': category}, {'manufacturer': 1,
#                                                         '_id': 0})
#     return set([vendor['manufacturer'] for vendor in vendors])


if __name__ == '__main__':
    pprint(DB.vendors.find_one({}))
