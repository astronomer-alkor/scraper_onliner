from pymongo import MongoClient
from pprint import pprint


def create_database_connection():
    client = MongoClient()
    return client.full_database


db = create_database_connection()


def get_products_preview():
    return [product for product in db.products.find({}, {'name': 1,
                                                         'description': 1,
                                                         'img_url': 1,
                                                         'current_price': 1,
                                                         'key': 1,
                                                         'category': 1,
                                                         '_id': 0
                                                         })][:20]


def get_product_data(product_name):
    return db.products.find_one({'key': product_name})


def get_all():
    pprint(db.products.find()[0])


if __name__ == '__main__':
    get_all()
