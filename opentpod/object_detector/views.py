import shutil
import json

from cvat.apps.authentication import auth
from django.db.models import Q
from django.shortcuts import render
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
import django_rq
import sendfile

from opentpod.object_detector import models, serializers
from opentpod.object_detector import tasks as bg_tasks
from opentpod.object_detector import provider
from rest_framework.response import Response
from django.http import Http404


class TrainSetViewSet(viewsets.ModelViewSet):
    queryset = models.TrainSet.objects.all()
    serializer_class = serializers.TrainSetSerializer
    search_fields = ("name", "owner__username")


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
        if self.request.data.get('owner', None):
            db_detector = serializer.save(status=models.Status.CREATED)
        else:
            db_detector = serializer.save(owner=self.request.user,
                                          status=models.Status.Created)

        db_detector.get_training_data_dir().mkdir(parents=True)
        db_detector.get_model_dir().mkdir(parents=True)
        bg_tasks.train(
            db_detector,
            self.request.user,
            self.request.scheme,
            self.request.get_host()
        )

    def perform_destroy(self, db_detector):
        shutil.rmtree(db_detector.get_dir())
        db_detector.delete()

    @action(detail=True, methods=['GET'])
    def status(self, request, pk):
        """Check Detector Status."""
        db_detector = self.get_object()
        cur_status = db_detector.get_status()
        return Response(data=json.dumps(cur_status))

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
        dnn_obj = dnn_class(config={'input_dir': '', 'output_dir': ''})
        required_parameters = dnn_obj.required_parameters
        optional_parameters = dnn_obj.optional_parameters
        data = json.dumps({
            'required': required_parameters,
            'optional': optional_parameters
        })
        return Response(data=data)

    @action(detail=True, methods=['GET', 'POST'])
    def model(self, request, pk):
        """Download Trained Model Data."""
        db_detector = self.get_object()
        if db_detector.status != models.Status.TRAINED.value:
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

    @action(detail=True, methods=['POST'])
    def visualization(self, request, pk):
        """Visualize Training Procedures.
        Currently only support tensorboard
        """
        db_detector = self.get_object()
        bg_tasks.visualize(db_detector)
        return Response(status=status.HTTP_202_ACCEPTED, data={json.dumps('created')})
        # queue = django_rq.get_queue("tensorboard")
        # rq_job = django_rq.get_current_job()
        # if request.method == 'GET':
        #     if rq_job:
        #         if rq_job.is_finished:
        #             return sendfile.sendfile(request, rq_job.meta["file_path"], attachment=True,
        #                                     attachment_filename=str(
        #                                         db_detector.get_export_file_path().name))
        #         elif rq_job.is_failed:
        #             exc_info = str(rq_job.exc_info)
        #             rq_job.delete()
        #             return Response(data=exc_info, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        #         else:
        #             return Response(status=status.HTTP_202_ACCEPTED, data={json.dumps('created')})
        #     else:
        #         raise Http404
