$(document).ready(function() {
    $('head', document).append('<link rel="stylesheet" type="text/css" media="screen" href="{{ STATIC_URL }}js/wymeditor/skins/default/screen.css" />');
    
    $("#id_text").wymeditor({
        updateSelector: "input:submit",
        updateEvent:    "click",
        postInit: function() {
            //alert('OK');
        }         
    });
});