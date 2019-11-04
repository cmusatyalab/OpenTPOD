from django.urls import path, include
from . import views

urlpatterns = [
    # Entry point for a client
    path("", views.render_cvat_annotation_ui),
]
