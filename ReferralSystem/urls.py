"""
URL configuration for ReferralSystem project.
"""

from django.contrib import admin
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Referral System",
        default_version='v1',
        description="Referral System API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("referral/", include('referral_system.urls')),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
