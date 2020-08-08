from django.contrib import admin
from django.contrib.admin import ModelAdmin as BaseModelAdmin
from django.utils.translation import gettext as _

from .models import User, Tag


class ModelAdmin(BaseModelAdmin):
    ordering = ['id']
    list_display = ['name', 'email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name', )}),
        (_('Permissions'),
         {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important Date'), {'fields': ('last_login', )})
    )

    add_fieldsets = (
        (None,
         {
             'classes': ('wide',),
             'fields': ('email', 'password1', 'password2')
         }),
    )


admin.site.register(User, ModelAdmin)
admin.site.register(Tag)
