from app.application import APP
from app.core.database import DB
from app.core.scraper import get_categories_structure
from app import view

if __name__ == '__main__':
    if not DB.list_collection_names():
        get_categories_structure()
    APP.run()
