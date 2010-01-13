from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

class BFAdmin(admin.ModelAdmin):
    """
    Model admin with default values for site and author
    fields
    """

    def queryset(self, request):
        qs = super(BFAdmin, self).queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(author=request.user)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        '''
        Overwrite get_form to select the currently logged in user as the author
        '''
        form = super(BFAdmin, self).get_form(request, obj, **kwargs)
        f = form.base_fields['author']
        f.initial = request.user.pk
        if request.user.is_superuser:
            f.queryset = User.objects.filter(is_staff=True)
        else:
            f.queryset = User.objects.filter(pk=request.user.pk)
        form.base_fields['site'].initial = Site.objects.get_current().pk
        return form

