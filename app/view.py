from flask import (
    render_template,
    redirect,
    request
)
from app.application import APP
from app.core.database import (
    get_products_preview,
    get_product_data,
    check_category,
    get_vendors_by_category
)
from app.core.api import (
    get_pagination,
    update_query_params
)


@APP.route('/categories/<category>/', methods=['GET', 'POST'])
def catalog(category):
    try:
        if not check_category(category):
            raise ValueError
        if set(request.args.keys()) - {'page', 'limit'}:
            raise ValueError
        page = int(request.args.get('page', default=1))
        limit = int(request.args.get('limit', default=30))
    except ValueError:
        if request.method == 'POST':
            return render_template('404_POST.html')
        return render_template('404.html')
    url = request.url
    if limit < 10 or limit > 50:
        return redirect(update_query_params(url, limit=30))
    if request.method == 'POST':
        return render_template('products.html',
                               products=get_products_preview(category, page=page, limit=limit),
                               pagination=get_pagination(page, limit, url, category=category))
    return render_template('index.html', vendors=get_vendors_by_category(category))


@APP.route('/<category>/<product_name>')
def product(category, product_name):
    return render_template('product.html', product=get_product_data(product_name))


@APP.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
