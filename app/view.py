from flask import (
    render_template,
    redirect,
    request
)
from app.application import APP
from app.core.database import (
    get_products_preview,
    get_product_data,
)
from app.core.api import (
    get_pagination,
    update_query_params
)


@APP.route('/')
def index():
    page = request.args.get('page', default=1)
    limit = request.args.get('limit', default=30)
    url = request.url
    try:
        limit = int(limit)
        if limit < 10 or limit > 50:
            return redirect(update_query_params(url, limit=30))
        page = int(page)
        return render_template('index.html', products=get_products_preview(page=page, limit=limit),
                               pagination=get_pagination(page, limit, url))
    except ValueError:
        return render_template('404.html')


@APP.route('/<category>/<product_name>')
def product(category, product_name):
    return render_template('product.html', product=get_product_data(product_name))
