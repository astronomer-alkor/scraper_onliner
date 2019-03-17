from app.application import app
from app.core.database import get_products_preview
from flask import render_template


@app.route('/')
def index():
    return render_template('index.html', products=get_products_preview())
