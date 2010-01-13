"""Realisation of rendering different markup languages"""

from markdown2 import Markdown
from bbcode import bb2xhtml

from render import textparser
from render.morefixer import more_fix
from typogrify.templatetags.typogrify import typogrify
from wikimarkup import parse as parseWiki

try:
    import docutils.core
    has_docutils = True
except ImportError:
    has_docutils = False


RENDER_METHODS = (
    ('markdown', 'Markdown'),
    ('bbcode', 'BB code'),
    ('html', 'HTML'),
    ('html_br', 'Text+HTML (livejournal)'),
    ('text', 'Plain text'),
    ('wikimarkup', 'MediaWiki markup'),
)

if has_docutils:
    RENDER_METHODS += (('rst', 'reStructuredText'), )

class RenderException(Exception):
    """Can't render"""
    pass

def render(content, render_method, unsafe=False):
    renderer = Renderer(content, render_method, unsafe)
    return renderer.render()


class Renderer(object):
    def __init__(self, content, render_method, unsafe=False):
        self.content = content.strip()
        self.render_method = render_method
        self.unsafe = unsafe

    def render(self):
        try:
            renderer = getattr(self, 'get_%s_render' % self.render_method)()
        except AttributeError:
            raise RenderException(u"Unknown render method: '%s'" % self.render_method)
        return unicode(typogrify(more_fix(renderer(self.content))))

    def get_markdown_render(self):
        md = Markdown(extras=['footnotes', 'code-friendly'], safe_mode=not self.unsafe and "escape")
        return md.convert

    def get_bbcode_render(self):
        return bb2xhtml

    def get_text_render(self):
        return textparser.to_html

    def get_html_render(self):
        return lambda x: x

    def get_html_br_render(self):
        return textparser.add_br

    def get_wikimarkup_render(self):
        return lambda text : parseWiki(text, showToc=True)

    def get_rst_render(self):
        if not has_docutils:
            raise RenderException(u"Docutils not found")

        def html_parts(input_string, source_path=None, destination_path=None,
                       input_encoding='unicode', doctitle=1, initial_header_level=1):
            overrides = {'input_encoding': input_encoding,
                         'doctitle_xform': doctitle,
                         'initial_header_level': initial_header_level}
            parts = docutils.core.publish_parts(
                source=input_string, source_path=source_path,
                destination_path=destination_path,
                writer_name='html', settings_overrides=overrides)
            return parts

        def html_body(input_string, source_path=None, destination_path=None,
                      input_encoding='unicode', output_encoding='unicode',
                      doctitle=1, initial_header_level=1):
            parts = html_parts(
                input_string=input_string, source_path=source_path,
                destination_path=destination_path,
                input_encoding=input_encoding, doctitle=doctitle,
                initial_header_level=initial_header_level)
            fragment = parts['html_body']
            if output_encoding != 'unicode':
                fragment = fragment.encode(output_encoding)
            return fragment

        return html_body
