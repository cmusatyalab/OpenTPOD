import pathlib
import json
import enum

from cvat.apps.engine.models import Task
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from opentpod.object_detector import provider


class Status(enum.Enum):
    CREATED = 'created'
    TRAINING = 'training'
    TRAINED = 'trained'
    ERRORED = 'error'

    @classmethod
    def choices(self):
        return tuple((x.value, x.name) for x in self)

    def __str__(self):
        return self.value


class TrainSet(models.Model):
    """A set of training videos.
    """
    name = models.CharField(max_length=256)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    tasks = models.ManyToManyField(Task)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Detector(models.Model):
    """Trained Detector
    """
    name = models.CharField(max_length=256)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, choices=Status.choices(),
                              default=str(Status.CREATED), null=True, blank=True)
    dnn_type = models.CharField(max_length=32,
                                choices=provider.DNN_TYPE_DB_CHOICES)
    # where this model is finetuned from
    parent = models.ForeignKey('self', null=True,
                               blank=True, on_delete=models.SET_NULL)
    train_set = models.ForeignKey(TrainSet, null=True,
                                  on_delete=models.SET_NULL)
    train_config = models.CharField(max_length=10000)
    # constants
    _CONTAINER_NAME_FORMAT = 'opentpod-detector-{}'

    class Meta:
        ordering = ['id']

    def __str__(self):
        return '{}-{}'.format(self.pk, self.name)

    def get_dir(self):
        return pathlib.Path(settings.VAR_DIR) / 'detectors' / str(self.id)

    def get_training_data_dir(self):
        return self.get_dir() / 'train-data'

    def get_model_dir(self):
        return self.get_dir() / 'models'

    def get_export_file_path(self):
        return self.get_dir() / '{}-frozen-graph.zip'.format(self.name)

    def get_container_name(self):
        return self._CONTAINER_NAME_FORMAT.format(self.id)

    def get_train_config(self):
        return json.loads(self.train_config)

    def get_detector_object(self):
        config = self.get_train_config()
        config['input_dir'] = self.get_training_data_dir().resolve()
        config['output_dir'] = self.get_model_dir().resolve()
        detector_class = provider.get(self.dnn_type)
        return detector_class(config)
