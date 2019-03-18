from app.application import app
from app.core.database import (
    get_products_preview,
    get_product_data
)
from flask import (
    render_template,
    request
)


@app.route('/')
def index():
    page = request.args.get('page', default=1, type=int)
    return render_template('index.html', products=get_products_preview(page=page))


@app.route('/<category>/<product_name>')
def product(category, product_name):
    return render_template('product.html', product=get_product_data(product_name))
