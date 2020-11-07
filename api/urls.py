from django.contrib import admin
from django.urls import path, include, re_path

# Swagger
from rest_framework import permissions
from drf_yasg2.views import get_schema_view
from drf_yasg2 import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="MyDesk API docs.",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),

    path('departments/', include('departments.urls')),
    path('classes/', include('classes.urls')),
    path('sections/', include('sections.urls')),
    path('subjects/', include('subjects.urls')),
    path('organizations/', include('organizations.urls')),
    path('teachers/', include('teachers.urls')),
    path('students/', include('students.urls')),

    re_path(r'^swagger(?P<format>.json|.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
