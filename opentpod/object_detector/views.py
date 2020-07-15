import json
import os
import shutil

import django_rq
import sendfile
from cvat.apps.authentication import auth
from cvat.apps.authentication.decorators import login_required
from cvat.apps.engine.models import Task
from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from proxy.views import proxy_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from opentpod.object_detector import models, provider, serializers
from opentpod.object_detector import tasks as bg_tasks
from logzero import logger
import zipfile

class TrainSetViewSet(viewsets.ModelViewSet):
    queryset = models.TrainSet.objects.all()
    serializer_class = serializers.TrainSetSerializer
    search_fields = ("name", "owner__username")

class DetectorModelViewSet(viewsets.ModelViewSet):
    queryset = models.DetectorModel.objects.all()
    serializer_class = serializers.DetectorModelSerializer
    search_fields = ("name", "owner__username")

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        # Don't filter queryset for admin
        if auth.has_admin_role(user) or self.detail:
            return queryset
        else:
            return queryset.filter(Q(owner=user)).distinct()
            
    def perform_create(self, serializer):
        selfmodel = serializer.save()

    def perform_destroy(self, selfmodel):
        logger.info('get delete in view')
        shutil.rmtree(selfmodel.getPath())
        selfmodel.delete()

    def setmodelt2default(seld, selfmodel):
        return selfmodel.getFilePath()
    #     logger.info("this is a test in view")
    #     currentModel = serializer.save()
    #     logger.info(currentModel.name)
    #     logger.info(currentModel.getPath())
        # with zipfile.ZipFile(currentModel.getPath(), 'r') as zip_ref:
        #     zip_ref.extractall()
        # if request.method == 'POST':
        #     logger.info("this is a post request")

    # def put(self, request, filename, format=None):
    #     logger.info("detail view")
    # def upload_file(request):
    #     logger.info("detail view")
    # def perform_destroy(self, currentModel):
    #     os.remove(currentModel.getPath())

class DetectorViewSet(viewsets.ModelViewSet):
    queryset = models.Detector.objects.all()
    serializer_class = serializers.DetectorSerializer
    search_fields = ("name", "owner__username", "status")
    ordering_fields = ("id", "name", "owner", "status")

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        # Don't filter queryset for admin
        if auth.has_admin_role(user) or self.detail:
            return queryset
        else:
            return queryset.filter(Q(owner=user)).distinct()

    def perform_create(self, serializer):
        db_detector = serializer.save()
        db_detector.get_training_data_dir().mkdir(parents=True)
        db_detector.get_model_dir().mkdir(parents=True)
        # db_detector.get_pretrain_dir().mkdir(parents=True)
        bg_tasks.train(
            db_detector,
            self.request.user,
            self.request.scheme,
            self.request.get_host()
        )

    def perform_destroy(self, db_detector):
        shutil.rmtree(db_detector.get_dir())
        db_detector.delete()

    @staticmethod
    @action(detail=False, methods=['GET'], url_path='types')
    def dnn_types(request):
        """Return supported dnn types.
        A list of tuples:
        [
        (detector type 1, human readable label 1),
        (detector type 2, human readable label 2),
        ]
        """
        dnn_types = provider.DNN_TYPE_DB_CHOICES
        return Response(data=json.dumps(dnn_types))

    @staticmethod
    @action(detail=False, methods=['GET'], url_path='training_configs/(?P<type>.+)')
    def training_configs(request, type):
        """Return required and optional training parameters for a type.
        A Dict:
        {
            'required': required parameter list,
            'optional': a dict of optional parameters and their default value.
        }
        """
        dnn_class = provider.get(type)
        if dnn_class is None:
            raise Http404
        data = json.dumps(dnn_class.TRAINING_PARAMETERS)
        return Response(data=data)

    @action(detail=True, methods=['GET', 'POST'])
    def model(self, request, pk):
        """Download Trained Model Data."""
        db_detector = self.get_object()
        if db_detector.status != str(models.Status.TRAINED):
            raise Http404('Model is not in TRAINED status. Current status: {}'.format(
                db_detector.status))

        queue = django_rq.get_queue("default")
        rq_id = "{}@/api/opentpod/v1/detectors/{}/data".format(
            self.request.user, pk)
        rq_job = queue.fetch_job(rq_id)

        if request.method == 'GET':
            if rq_job:
                if rq_job.is_finished:
                    return sendfile.sendfile(request, rq_job.meta["file_path"], attachment=True,
                                             attachment_filename=str(
                        db_detector.get_export_file_path().name))
                elif rq_job.is_failed:
                    exc_info = str(rq_job.exc_info)
                    rq_job.delete()
                    return Response(data=exc_info, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response(status=status.HTTP_202_ACCEPTED, data={json.dumps('created')})
            else:
                raise Http404
        if request.method == 'POST':
            rq_job = queue.enqueue_call(
                func=bg_tasks.export,
                args=(db_detector,),
                job_id=rq_id,
            )
            rq_job.meta["file_path"] = db_detector.get_export_file_path()
            rq_job.save_meta()
            return Response(status=status.HTTP_202_ACCEPTED, data={json.dumps('created')})

    @action(detail=True,
            methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
            url_path='visualization/(?P<remote_path>.+)')
    def visualization(self, request, pk, remote_path):
        """Model visualization. Proxying requests to individual
        provider to render visualization in web UI.
        """
        db_detector = self.get_object()
        detector = db_detector.get_detector_object()
        return detector.visualize(request, remote_path)


@login_required
def task_data(request, task_id, data_path):
    """serving user's task data with permission checking.
    CVAT doesn't provide APIs to access all task data, e.g. uploaded videos.
    Using django-xsendfile in order to serve files with web server
    https://github.com/johnsensible/django-sendfile
    """
    db_tasks = Task.objects.filter(pk=task_id)
    if not auth.has_admin_role(request.user):
        db_tasks.filter(Q(owner=request.user))
    if len(db_tasks) < 1:
        raise Http404
    db_task = db_tasks[0]
    file_path = os.path.abspath(os.path.realpath(os.path.join(db_task.get_task_dirname(), data_path)))
    return sendfile.sendfile(request, file_path)
