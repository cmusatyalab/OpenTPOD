from cvat.apps.authentication.decorators import login_required
from django.http import Http404
from django.shortcuts import render


@login_required
def render_cvat_annotation_ui(request):
    """An entry point to dispatch legacy requests"""
    if request.method == 'GET' and 'id' in request.GET:
        return render(request, 'engine/annotation.html')
    raise Http404("Annotation UI Not Found. Did you specify a video ID?")
