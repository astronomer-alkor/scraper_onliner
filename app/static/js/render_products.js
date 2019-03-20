function get_products(url) {
    $.ajax({
        type: 'POST',
        url: url,
        success: function (products) {
            console.log(products);
            $('.products_block').html(products);
        }
    });
}

$(document).ready(function () {
    let url = $(location).attr('href');
    get_products(url);
});


$(document).delegate('a.pagination_link', 'click', function (event) {
    event.preventDefault();
    let url = $(this).attr('href');
    get_products(url);
});