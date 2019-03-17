from pymongo import MongoClient
from pprint import pprint


def create_database_connection():
    client = MongoClient()
    return client.test7_database


db = create_database_connection()


def get_products_preview():
    return [product for product in db.products.find({}, {'name': 1,
                                                         'description': 1,
                                                         'img_url': 1,
                                                         '_id': 0
                                                         })]


def get_all():
    pprint(db.products.find()[0])


if __name__ == '__main__':
    get_all()
