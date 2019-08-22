# modified by junjuew
# Copyright (C) 2018 Intel Corporation
#
# SPDX-License-Identifier: MIT

from django.urls import path, include
from rest_framework import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from opentpod.object_detector import views

schema_view = get_schema_view(
    openapi.Info(
        title="OpenTPOD REST API",
        default_version='v1',
        description="REST API for Opensource Tool For Painless Object Detection (OpenTPOD)",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="junjuew@cs.cmu.edu"),
        license=openapi.License(name="Apache V2 License"),
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
)

router = routers.DefaultRouter(trailing_slash=False)
router.register('detectors', views.DetectorViewSet)

urlpatterns = [
    # documentation for API
    path('api/swagger.<slug:format>$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/v1/', include((router.urls)))
]
