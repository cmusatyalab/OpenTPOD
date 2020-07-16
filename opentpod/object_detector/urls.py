from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from opentpod.object_detector import views

from django.conf import settings
from django.conf.urls.static import static

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
router.register('trainsets', views.TrainSetViewSet)
router.register('detectormodels', views.DetectorModelViewSet)

urlpatterns = [
    # documentation for API
    path('api/opentpod/swagger.<slug:format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/opentpod/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/opentpod/docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/opentpod/v1/', include((router.urls))),
    # for serving data files
    path('task_data/<int:task_id>/<path:data_path>', views.task_data),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.TRAINMODEL_URL, document_root=settings.TRAINMODEL_ROOT)
