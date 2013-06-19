from django.contrib import admin
from django.conf import settings
from pinry.pins.models import Pin
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import HttpResponse
from django.template.response import TemplateResponse

from django.utils.translation import ugettext as _
from django.contrib.admin import helpers
from django.template.loader import render_to_string, get_template
from django.contrib.sites.models import Site

from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.contrib import messages


class PinAdmin(admin.ModelAdmin):
    list_display = ['pk', 'admin_thumb', 'submitter', 'smartdate', 'published', 'description', 'imgName', 'imgUrl', 'srcUrl']

admin.site.register(Pin, PinAdmin)

def send_email(self, request, queryset):
    current_site = Site.objects.get_current()
    if request.POST.get('post'):
        if len(queryset)>0:
            for u in queryset:
                message = request.POST['message']
                subject = request.POST['subject']
                from_email = request.POST['from_email']
                recipient_format = getattr(settings, 'EMAIL_RECIPIANT_NAME', 'username')
                recipient = getattr(u, recipient_format)
                context = {'recipient': recipient,
                           'first_name': u.first_name,
                           'last_name': u.last_name,
                           'message':mark_safe(message),
                           'preform':True,
                           'site': current_site,}
                html_content = render_to_string('email/email_generic.html',context)
                context.update({'message':mark_safe(strip_tags(message))})
                email_body = render_to_string('email/email_generic.txt',context)
                
                msg = EmailMultiAlternatives(subject, email_body, from_email,[u.email])
                msg.attach_alternative(html_content, "text/html")
                try:
                    msg.send()
                except:
                    messages.error(request, "Mail to %s : %s failed" % (str(u),u.email))
                    #self.message_user(request, "There was a problem sending the email to: "+str(u)+" at:"+ u.email)
                messages.success(request, "Mail has been sent")
        else:
            self.message_user(request, "No Recipiants were selected")
    else:
        context = {
            'title': _("Email Users"),
            'queryset': queryset,
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            'html_preview': render_to_string('email/email_generic.html',
                           {'recipient': 'recipient',
                            'preform':True,
                            'message':'--your note will be inserted here--',
                            'site': current_site,}),
            'text_preview': render_to_string('email/email_generic.txt',
                           {'recipient': 'recipient',
                            'preform':True,
                            'message':'--your note will be inserted here--',
                            'site': current_site,})
        }
        return TemplateResponse(request, 'email/email_users.html',
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
