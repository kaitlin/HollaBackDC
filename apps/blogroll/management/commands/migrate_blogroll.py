from django.core.management import base, color
from django.utils import termcolors
import sys

def color_style():
    style = color.color_style()
    style.ALREADY = termcolors.make_style(fg='yellow')
    style.OK = termcolors.make_style(fg='green', opts=('bold'),)
    style.REGULAR = termcolors.make_style()

    return style

def out(style, msg, newline=False):
    sys.stdout.write(style(msg))
    if newline:
        sys.stdout.write('\n')
    sys.stdout.flush()

class Command(base.NoArgsCommand):
    help = "Copy blogroll data to friends"

    def handle_noargs(self, **options):
        from blogroll.models import Link
        from friends.models import FriendBlog
        identical_fields = ('site', 'name', 'weight')
        mapped_fields = {
            # friends' field: blogroll's field
            'author': 'user',
            'link': 'url',
            'rel_friendship': 'friendship_rel',
            'rel_professional': 'professional_rel',
            'rel_geographical': 'geographical_rel',
            'rel_family': 'family_rel',
            'rel_romantic': 'romantic_rel',
            'rel_identity': 'identity_rel',
        }
        style = color_style()
        for item in Link.objects.all():
            # identical field names
            out(style.REGULAR, item.url)
            data = dict((key, getattr(item, key)) for key in identical_fields if getattr(item, key))
            for f_field, br_field in mapped_fields.items():
                data[f_field] = getattr(item, br_field)
            created = False
            friend, created = FriendBlog.objects.get_or_create(**data)
            if created:
                out(style.REGULAR, ' exploring ')
                friend.save()
                out(style.REGULAR, '->%s' % friend.feed)
                out(style.OK, ' OK', True)
            else:
                out(style.ALREADY, ' SKIPPED, already copied', True)

