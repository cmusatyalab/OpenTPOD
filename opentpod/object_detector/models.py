import pathlib
from enum import Enum

from cvat.apps.engine.models import Video
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from opentpod.object_detector import provider


class Status(Enum):
    CREATED = 'created'
    TRAINING = 'training'
    TRAINED = 'trained'

    @classmethod
    def choices(self):
        return tuple((x.value, x.name) for x in self)

    def __str__(self):
        return self.value


class TrainSet(models.Model):
    name = models.CharField(max_length=256)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    videos = models.ManyToManyField(Video)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Detector(models.Model):
    name = models.CharField(max_length=256)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, choices=Status.choices(),
                              default=Status.CREATED)
    dnn_type = models.CharField(max_length=32,
                                choices=provider.DNN_TYPE)
    # where this model is finetuned from
    parent = models.ForeignKey('self', null=True,
                               blank=True, on_delete=models.SET_NULL)
    trainset = models.ForeignKey(TrainSet, null=True,
                                 on_delete=models.SET_NULL)

    # constants
    _CONTAINER_NAME_FORMAT = 'opentpod-detector-{}'

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_dir(self):
        return pathlib.Path(settings.DATA_ROOT) / 'detector' / str(self.id)

    def get_container_name(self):
        return self._CONTAINER_NAME_FORMAT.format(self.id)
