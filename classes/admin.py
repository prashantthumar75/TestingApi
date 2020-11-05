from django.contrib import admin
from django.apps import apps

admin.site.register(apps.get_app_config('classes').get_models())