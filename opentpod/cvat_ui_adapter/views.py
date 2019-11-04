from django.shortcuts import render
from cvat.apps.authentication.decorators import login_required
from cvat.apps.engine.models import StatusChoice
from cvat.settings.base import JS_3RDPARTY, CSS_3RDPARTY


@login_required
def render_cvat_annotation_ui(request):
    """An entry point to dispatch legacy requests"""
    if request.method == 'GET' and 'id' in request.GET:
        return render(request, 'engine/annotation.html', {
            'css_3rdparty': CSS_3RDPARTY.get('engine', []),
            'js_3rdparty': JS_3RDPARTY.get('engine', []),
            'status_list': [str(i) for i in StatusChoice]
        })
