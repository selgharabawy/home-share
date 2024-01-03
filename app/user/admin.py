"""
Django admin customization
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from user import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name', 'gender', 'user_type']
    fieldsets = (
        (
            None, {
                'fields': (
                    'email',
                    'password',
                    'name',
                    'gender',
                    'user_type'
                )
            }
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                        'email',
                        'password1',
                        'password2',
                        'name',
                        'gender',
                        'user_type',
                        'is_active',
                        'is_staff',
                        'is_superuser',
            )
        }),
    )


admin.site.register(models.User, UserAdmin)
