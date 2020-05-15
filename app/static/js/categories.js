$(document).ready(function () {
    $('#Электроника').addClass('main_category--current');
    $('.main_category_button[name="Электроника"]').addClass('main_category_button--current');
    $($('.subcategory__title')[0]).addClass('subcategory__title--current');
    $($('.subcategory__title')[0]).next().addClass('subcategory_block--current');
});

$('.main_category_button').click(function() {
    let category = $(this).attr('name');
    $('.main_category_button').removeClass('main_category_button--current');
    $(this).addClass('main_category_button--current');
    $('.main_category').removeClass('main_category--current');
    $('.main_category[id="' + category + '"]').addClass('main_category--current');
});

$('.subcategory__title').hover(function () {
    $('.subcategory__title').removeClass('subcategory__title--current');
    $('.subcategory_block').removeClass('subcategory_block--current');
    $(this).addClass('subcategory__title--current');
    $(this).next().addClass('subcategory_block--current');
});