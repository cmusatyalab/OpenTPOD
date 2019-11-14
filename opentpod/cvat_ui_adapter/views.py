from cvat.apps.authentication.decorators import login_required
from cvat.apps.engine.models import StatusChoice
from cvat.settings.base import CSS_3RDPARTY, JS_3RDPARTY
from django.http import Http404
from django.shortcuts import render


@login_required
def render_cvat_annotation_ui(request):
    """An entry point to dispatch legacy requests"""
    if request.method == 'GET' and 'id' in request.GET:
        return render(request, 'engine/annotation.html', {
            'css_3rdparty': CSS_3RDPARTY.get('engine', []),
            'js_3rdparty': JS_3RDPARTY.get('engine', []),
            'status_list': [str(i) for i in StatusChoice]
        })
    raise Http404("Annotation UI Not Found. Did you specify a video ID?")
