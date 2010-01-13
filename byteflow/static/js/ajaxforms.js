function ajaxFormTest(form) {
    var postData = $(form).formToArray()
    postData[postData.length] = {'name': '_ajax', 'value': true}
    var url = $(form).attr('action') ? form.action : location
    $.post(url, postData, function(data) {
        var json = eval('(' + data + ')')
        showErrors(form, json.errors)
        if (json.valid) {
            form.submit()
        }
    })
    return false
}

function getInputErrorList(form, input_name) {
    if ('__all__' == input_name) {
        var prevUL = $(form).prev()
        if (prevUL && 'errorlist' == prevUL.attr('class')) {
            return prevUL;
        }
        var errorList = $('<ul class="errorlist"></ul>')
        $(form).before(errorList)
        return errorList
    }
    var input = $('[name="' + input_name + '"]', form)
    /* This is hack for MultiValud Fields */
    if ('undefined' == typeof(input[0])) {
        var input = $('[name="' + input_name + '_0"]', form)
    }
    if ('undefined' == typeof(input[0])) {
        return null;
    }
    /* Following code could be used when django form generation
     * will support invalid class adding to fields with invalid data
     */
    //} else {
        //input.addClass('invalid');
    //}
    var prevUL = $(input).parent().prev()
    if (prevUL && prevUL.attr('class') == 'errorlist') {
        return prevUL
    }
    var errorList = $('<ul class="errorlist"></ul>')
    $(input).parent().before(errorList)
    return errorList
}

function showErrors(form, errors) {
    $('.errorlist').empty()
    for (var field in errors) {
        var errorList = getInputErrorList(form, field)
        if (errorList) {
            $.each(errors[field], function(i, error) {
                $(errorList).append('<li>' + error + '</li>')
            })
        }
    }
}
