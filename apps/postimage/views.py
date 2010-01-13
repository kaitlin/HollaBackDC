from django.template import Context, RequestContext, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

from postimage.forms import AttachForm, UploadForm


@user_passes_test(lambda u: u.is_staff)
@never_cache
def select(request):
    '''
    Just pass back the form, we do only javascript magic
    '''
    t = loader.get_template('admin/postimage/attach.html')

    form = AttachForm(initial={'file': request.GET.get('s')})
    c = { 'title': _('Attach file'),
         'form': form,
         'media_url': settings.STATIC_URL,
         'postimage_url': settings.POSTIMAGE_URL,
         'postimage_root': settings.POSTIMAGE_ROOT,
         'for': request.GET['for'], }
    c = RequestContext(request, c)
    return HttpResponse(t.render(c))


@user_passes_test(lambda u: u.is_staff)
def upload(request):
    '''
    Upload a new file
    '''
    t = loader.get_template('admin/postimage/upload.html')
    form = request.method=='POST' and UploadForm(request.POST, request.FILES) or UploadForm()

    if form.is_valid():
        file = form.save()
        return HttpResponseRedirect(''.join((
                    reverse('postimage_attach'),
                    '?s=%s&amp;for=%s' % (file, request.POST.get('for'))
                    )))

    c = Context({ 'title': _('Upload file'), 'form': form, 'for': request.GET.get('for')})
    return HttpResponse(t.render(c))

