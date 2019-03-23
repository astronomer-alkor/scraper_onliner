from app.application import APP
from app.core.database import DB
from app.core.scraper import get_categories_structure
from app import view

if __name__ == '__main__':
    if not DB.collection_names(include_system_collections=False):
        get_categories_structure()
    APP.run()
