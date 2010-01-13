import os

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _


def handle_uploaded_file(file, to):
    if not os.path.exists(to):
        os.makedirs(to, 0777)
    path = os.path.join(to, file.name)
    destination = open(path, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    return path


class AttachForm(forms.Form):
    alt = forms.CharField(label=_('Description'), initial=_('Image'))

    def __init__(self, *args, **kwargs):
        super(AttachForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FilePathField(label=_('Select a file to attach'),
                                                  path=settings.POSTIMAGE_ROOT, recursive=True,
                                                  required=True, initial=kwargs['initial']['file'])


class UploadForm(forms.Form):
    subdirectory = forms.CharField(label=_('Subdirectory'), required=False)
    file = forms.FileField(label=_('Select a file to attach'), required=True)

    def clean_subdirectory(self):
        self.cleaned_data['subdirectory'] = self.cleaned_data['subdirectory'].strip(os.path.pathsep)
        if self.cleaned_data['subdirectory'].find('.') != -1:
            raise forms.ValidationError, _("The subdirectory can't contain dots (.)")
        return os.path.join(settings.POSTIMAGE_ROOT, self.cleaned_data['subdirectory'])

    def save(self):
        return handle_uploaded_file(self.cleaned_data['file'], self.cleaned_data['subdirectory'])
