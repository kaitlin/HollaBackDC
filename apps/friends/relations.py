from django.utils.translation import ugettext_lazy as _

FRIENDSHIP_REL = (
    ('contact', _('contact')),
    ('acquaintance', _('acquaintance')),
    ('friend', _('friend')),
)

PHYSICAL_REL = (
    ('met', _('met')),
)

PROFESSIONAL_REL = (
    ('co-worker', _('co-worker')),
    ('colleague', _('colleague')),
)

GEOGRAPHICAL_REL = (
    ('co-resident', _('co-resident')),
    ('neighbor', _('neighbor')),
)

FAMILY_REL = (
    ('child', _('child')),
    ('parent', _('parent')),
    ('sibling', _('sibling')),
    ('spouse', _('spouse')),
    ('kin', _('kin')),
)

ROMANTIC_REL = (
    ('muse', _('muse')),
    ('crush', _('crush')),
    ('date', _('date')),
    ('sweetheart', _('sweetheart')),
)

IDENTITY_REL = (
    ('me', _('me')),
)
