$(document).ready(function($) {
    var Body = $('.preloader-wrapper');
    Body.addClass('preloader-wrapper_run');
});
$(window).load(function() {
    $('.preloader-wrapper').fadeOut();
    $('.preloader-wrapper').removeClass('preloader-wrapper_run');
});