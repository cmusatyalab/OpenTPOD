from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

# CVAT engine.urls is redirecting 'unknown url' to /dashboard/ which
# messes with our routing of unknown paths to index.html for reactjs
# so we have to strip the client entry point from cvat url patterns
from cvat.apps.engine.urls import urlpatterns as cvat_urlpatterns
cvat_urlpatterns = cvat_urlpatterns[1:]

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # use CVAT for labeling
    #path("", include("cvat.apps.engine.urls")),
    path("", include(cvat_urlpatterns)),
    path("cvat-ui", include("opentpod.cvat_ui_adapter.urls")),
    # use rest_auth for authentication and registration
    path("auth/", include("rest_auth.urls")),
    path("auth/registration/", include('rest_auth.registration.urls')),
    path("django-rq/", include('django_rq.urls')),
    path("", include("opentpod.object_detector.urls")),
    # React SPA
    path("manifest.json", TemplateView.as_view(template_name="manifest.json")),
    path("favicon.ico", default_views.page_not_found,
         kwargs={"exception": Exception("Page not Found")}),
    re_path(".*", TemplateView.as_view(template_name="index.html")),
] + static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
)
# + static(  # django only serves static files when DEBUG=True
#     settings.DATA_URL,
#     document_root=settings.DATA_ROOT
# )
# + static(
#     settings.MEDIA_URL,
#     document_root=settings.MEDIA_ROOT
# )

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
