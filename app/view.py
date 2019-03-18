from app.application import app
from app.core.database import (
    get_products_preview,
    get_product_data
)
from flask import render_template


@app.route('/')
def index():
    return render_template('index.html', products=get_products_preview())


@app.route('/<category>/<product_name>')
def product(category, product_name):
    return render_template('product.html', product=get_product_data(product_name))
