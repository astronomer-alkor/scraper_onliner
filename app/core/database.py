from pymongo import MongoClient
from pprint import pprint


def create_database_connection():
    client = MongoClient()
    return client.database


db = create_database_connection()


def get_products_preview(page=1, limit=30):
    skip = (page - 1) * 30
    return db.products.find({}, {'name': 1,
                                 'description': 1,
                                 'img_url': 1,
                                 'current_price': 1,
                                 'key': 1,
                                 'category': 1,
                                 '_id': 0
                                 }).skip(skip).limit(limit)


def get_product_data(product_name):
    return db.products.find_one({'key': product_name})


def get_all():
    pprint(len([i for i in db.products.find().skip(1).limit(30)]))


if __name__ == '__main__':
    get_all()
