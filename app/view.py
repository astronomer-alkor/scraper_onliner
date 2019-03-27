import time
from flask import (
    render_template,
    request
)
from app.application import APP
from app.core.database import (
    get_products_preview,
    get_product_data,
    check_category,
    get_vendors_by_category,
    parse_data,
    get_categories_structure,
    get_one_product_by_category,
    get_prices_by_category
)
from app.core.api import get_pagination


@APP.route('/')
def index():
    return render_template('index.html', structure=get_categories_structure())


@APP.route('/categories/<category>/', methods=['GET', 'POST'])
def catalog(category):
    try:
        if not check_category(category) or not get_one_product_by_category(category):
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
        limit = 30
    if request.method == 'POST':
        data = parse_data(request.get_json())
        time.sleep(1)
        products = list(get_products_preview(category, fields=data, page=page, limit=limit))
        if not products:
            return '<div class="not_found">К сожалению, по вашему запросу не нашлось продуктов.\n ' \
                   'Пожалуйста, измените критерии поиска</div>'

        return render_template('products.html', products=products,
                               pagination=get_pagination(page, limit, url, category=category, **data))

    return render_template('catalog.html', vendors=get_vendors_by_category(category), category=category,
                           prices=get_prices_by_category(category))


@APP.route('/<category>/<product_name>')
def product(category, product_name):
    return render_template('product.html', product=get_product_data(product_name),
                           prev_url=f'/categories/{category}')


@APP.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
