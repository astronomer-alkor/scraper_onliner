function get_products(url = '', data = {}) {
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
    data['single'] = {};
    let fields = $('input.field:checked');
    for (let i = 0; i < fields.length; i++) {
        let key = $(fields[i]).attr('about');
        let value = $(fields[i]).attr('name');
        if (!(key in data['single'])) {
            data['single'][key] = [];
        }
        data['single'][key].push(value);
    }
    data['ranges'] = {};
    let pairs = $('.filter_fields_range');
    for (let i = 0; i < pairs.length; i++) {
        let item = $(pairs[i]);
        data['ranges'][item.attr('about')] = {};
        let ranges = item.find('input');
        data['ranges'][item.attr('about')] = {};
        for (let j = 0; j < ranges.length; j++) {
            let value = $(ranges[j]);
            let key = value.attr('name');
            if (value.val()) {
                data['ranges'][item.attr('about')][key] = value.val();
            }
        }
    }
    console.log(data);
    return data
}

$(document).ready(function () {
    let url = $(location).attr('href');
    get_products(url, {});
    $(function () {
        $('.field_date_js').datepicker({
            changeYear: true,
            // showButtonPanel: true,
            dateFormat: 'yy',
            autoclose: true,
            onClose: function (dateText, inst) {
                var year = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
                $(this).datepicker('setDate', new Date(year, 1));
                let data = get_filters();
                get_products('', data);
            }
        });
        $(".date-picker-year").focus(function () {
            $(".ui-datepicker-month").hide();
        });
    });
});


$('input.field').on('change', function () {
    let data = get_filters();
    get_products('', data);
});


$('input.field_range').on('keyup', function () {
    let data = get_filters();
    get_products('', data);
});


$(document).delegate('a.pagination_link', 'click', function (event) {
    event.preventDefault();
    let url = $(this).attr('href');
    let data = get_filters();
    get_products(url, data);
});