from django.utils.html import escape

def to_html(data):
    data = add_br(escape(data))
    return data

def add_br(data):
    data = data.replace('\n', '<br/>\n')
    return data
