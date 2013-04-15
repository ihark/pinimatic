from django.contrib import admin
from django.conf import settings
from pinry.pins.models import Pin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.response import TemplateResponse

from django.utils.translation import ugettext as _
from django.contrib.admin import helpers
from django.template.loader import render_to_string, get_template
from django.contrib.sites.models import Site

class PinAdmin(admin.ModelAdmin):
    list_display = ['pk', 'id', 'submitter', 'published', 'description', 'imgName', 'imgUrl', 'srcUrl']

admin.site.register(Pin, PinAdmin)

def send_email(self, request, queryset):
    current_site = Site.objects.get_current()
    if request.POST.get('post'):
        if len(queryset)>0: 
            for u in queryset:
                message = request.POST['message']
                subject = request.POST['subject']
                from_email = request.POST['from_email']
                email_body = render_to_string('email/one_off.txt',
                               {'username': u.username,
                                'first_name': u.first_name,
                                'last_name': u.last_name,
                                'message':message,
                                'site': current_site,})
                send_mail(subject, email_body, from_email,[u.email] , fail_silently=False)
                self.message_user(request, "Mail sent successfully")
        else:
            self.message_user(request, "No Recipiants were selected")
    else:
        context = {
            'title': _("Email Users"),
            'queryset': queryset,
            'email_suffix': settings.DEFAULT_FROM_EMAIL,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            'template': get_template('email/one_off.txt'),
            'preview': render_to_string('email/one_off.txt',
                           {'username': 'username',
                            'message':'--your messeage above will be inserted here--',
                            'site': current_site,})
        }
        return TemplateResponse(request, 'core/email_users.html',
            context, current_app=self.admin_site.name)
                
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'id', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser']
    list_filter = [
        'is_staff', 'is_superuser']
    actions = [
        send_email,
    ]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
