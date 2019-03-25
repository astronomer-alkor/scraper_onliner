function get_products(url='', data={}) {
    let preloader = $('.preloader-wrapper');
    preloader.addClass('preloader-wrapper_run');
    $('.products_block').html('');
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: url,
        data: JSON.stringify(data),
        success: function (products) {
            $('.products_block').html(products);
            preloader.removeClass('preloader-wrapper_run');
        }

    });
}

function get_filters() {
    let data = {};
    let fields = $('input.field:checked');
    for (let i = 0; i < fields.length; i++) {
        let key = $(fields[i]).attr('about');
        let value = $(fields[i]).attr('name');
        if (!(key in data)) {
            data[key] = [];
        }
        data[key].push(value);
    }
    console.log(data);
    return data
}

$(document).ready(function () {
    let url = $(location).attr('href');
    get_products(url, {});
});


$('input.field').change(function() {
    let data = get_filters();
    get_products('', data);

});


$(document).delegate('a.pagination_link', 'click', function (event) {
    event.preventDefault();
    let url = $(this).attr('href');
    let data = get_filters();
    get_products(url, data);
});