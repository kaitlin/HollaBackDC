$(document).ready(custom_init);

function custom_init () {
    $('body').append('<img style="display: none;" src="{{ STATIC_URL }}img/ajaxload.gif" id="ajaxload" />');
}
