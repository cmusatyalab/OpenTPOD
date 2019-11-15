from cvat.apps.authentication import auth
from django.db.models import Q
from django.shortcuts import render
from rest_framework import permissions, viewsets

from opentpod.object_detector import models, serializers
from opentpod.object_detector import tasks as bg_tasks


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
        trainset_pk = self.request.data.get('trainset')
        trainset = models.TrainSet.objects.get(pk=trainset_pk)
        if self.request.data.get('owner', None):
            db_detector = serializer.save()
        else:
            db_detector = serializer.save(owner=self.request.user)

        db_detector.get_dir().mkdir(parents=True)
        # get labeled data
        bg_tasks.prepare_data(
            db_detector.get_dir(),
            trainset, self.request.user,
            self.request.scheme, self.request.get_host()
        )
        # launch training

    # @staticmethod
    # @action(detail=True, methods=['GET'], serializer_class=JobSerializer)
    # def jobs(request, pk):
    #     queryset = Job.objects.filter(segment__task_id=pk)
    #     serializer = JobSerializer(queryset, many=True,
    #         context={"request": request})

    #     return Response(serializer.data)

    # @action(detail=True, methods=['POST'], serializer_class=TaskDataSerializer)
    # def data(self, request, pk):
    #     db_task = self.get_object()
    #     serializer = TaskDataSerializer(db_task, data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #         task.create(db_task.id, serializer.data)
    #         return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    # @action(detail=True, methods=['GET'], serializer_class=RqStatusSerializer)
    # def status(self, request, pk):
    #     response = self._get_rq_response(queue="default",
    #         job_id="/api/{}/tasks/{}".format(request.version, pk))
    #     serializer = RqStatusSerializer(data=response)

    #     if serializer.is_valid(raise_exception=True):
    #         return Response(serializer.data)

    # @staticmethod
    # def _get_rq_response(queue, job_id):
    #     queue = django_rq.get_queue(queue)
    #     job = queue.fetch_job(job_id)
    #     response = {}
    #     if job is None or job.is_finished:
    #         response = { "state": "Finished" }
    #     elif job.is_queued:
    #         response = { "state": "Queued" }
    #     elif job.is_failed:
    #         response = { "state": "Failed", "message": job.exc_info }
    #     else:
    #         response = { "state": "Started" }
    #         if 'status' in job.meta:
    #             response['message'] = job.meta['status']

    #     return response
