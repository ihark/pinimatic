from django.contrib import admin

from pinry.pins.models import Pin


class PinAdmin(admin.ModelAdmin):
    list_display = ['pk', 'id', 'submitter', 'published', 'description']


admin.site.register(Pin, PinAdmin)
