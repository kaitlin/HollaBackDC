# -*- mode: python; coding: utf-8; -*-

from django import template
from django.conf import settings
from django.contrib.sites.models import Site

register = template.Library()

SOCIAL_BOOKMARK_TEMPLATES = {
    'google': ('Google', 'http://www.google.com/bookmarks/mark?op=add&title=&bkmk=%(url)s&labels=&annotation=%(title)s', 'google_002.png'),
    'slashdot': ('Slashdot', 'http://www.slashdot.org/bookmark.pl?url=%(url)s&title=%(title)s', 'slashdot.gif'),
    'yahoo': ('Yahoo', 'http://myweb2.search.yahoo.com/myresults/bookmarklet?u=%(url)s&t=%(title)s', 'yahoomyweb.png'),
    'digg': ('Digg', 'http://digg.com/submit?url=%(url)s', 'digg.gif'),
    'technorati': ('Technorati', 'http://technorati.com/faves?add=%(url)s', 'technorati.png'),
    'delicious': ('Delicious', 'http://del.icio.us/post?v=4&noui&jump=close&url=%(url)s&title=%(title)s', 'delicious.gif'),
    'bobrdobr': ('Bobrdobr.ru', 'http://www.bobrdobr.ru/addext.html?url=%(url)s&title=%(title)s', 'bobr_sml_red_3.gif'),
    'newsland': ('Newsland.ru', 'http://www.newsland.ru/News/Add/', 'newsland.gif'),
    'smi2': ('Smi2.ru', 'http://smi2.ru/add/', 'smi2.gif'),
    'rumarkz': ('Rumarkz.ru', 'http://rumarkz.ru/bookmarks/?action=add&popup=1&address=%(url)s&title=%(title)s', 'rumark.png'),
    'vaau': ('Vaau.ru', 'http://www.vaau.ru/submit/?action=step2&url=%(url)s', 'vaau.gif'),
    'memori': ('Memori.ru', 'http://memori.ru/link/?sm=1&u_data[url]=%(url)s&u_data[name]=%(title)s', 'memori.gif'),
    'rucity': ('Rucity.com', 'http://www.rucity.com/bookmarks.php?action=add&address=%(url)s&title=%(title)s', 'rucity.gif'),
    'moemesto': ('Moemesto.ru', 'http://moemesto.ru/post.php?url=%(url)s&title=%(title)s', 'mm.gif'),
    'news2': ('News2.ru', 'http://news2.ru/add_story.php?url=%(url)s', 'news2ru.png'),
    'mister-wong': ('Mister-Wong.ru', 'http://www.mister-wong.ru/index.php?action=addurl&bm_url=%(url)s&bm_description=%(title)s', 'mister-wong.gif'),
    'yandex': ('Yandex.ru', 'http://zakladki.yandex.ru/userarea/links/addfromfav.asp?bAddLink_x=1&lurl=%(url)s&lname=%(title)s', 'yandex-zakladki.gif'),
    'myscoop': ('Myscoop.ru', 'http://myscoop.ru/add/?URL=%(url)s&title=%(title)s', 'myscoop.gif'),
    '100zakladok': ('100zakladok.ru', 'http://www.100zakladok.ru/save/?bmurl=%(url)s&bmtitle=%(title)s', '100zakladok.gif'),
    'reddit': ('Reddit', 'http://reddit.com/submit?url=%(url)s&title=%(title)s', 'reddit.png'),
    'wykop': ('Wykop', 'http://www.wykop.pl/dodaj?url=%(url)s&title=%(title)s', 'wykop.gif'),
    'gwar': ('Gwar', 'http://www.gwar.pl/DodajGwar.html?u=%(url)s', 'gwar.gif'),
}

@register.inclusion_tag('blog/bookmarks.html', takes_context=True)
def bookmarks(context, post):
    url = '%s://%s%s' % (settings.SITE_PROTOCOL,
                         Site.objects.get_current().domain,
                         post.get_absolute_url())
    sites = []
    for key in settings.SOCIAL_BOOKMARKS:
        site = SOCIAL_BOOKMARK_TEMPLATES[key]
        sites.append({'name': site[0], 'url': site[1] % {'title': post.name,  'url': url},
                      'image': site[2]})
    return {'sites': sites, 'STATIC_URL': context['STATIC_URL']}
