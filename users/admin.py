from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ("provider",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ("provider",)}),
    )


admin.site.register(User, CustomUserAdmin)
