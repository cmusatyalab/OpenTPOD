import pathlib
import json
import enum
import os
from cvat.apps.engine.models import Task
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver

# from jobqueue import job_function, job_status, job_progress

from opentpod.object_detector import provider
from django.core.files.storage import FileSystemStorage
from logzero import logger

import shutil
import zipfile
import threading
import os.path
import time
import concurrent.futures

from opentpod.object_detector.helper import Zip2Model

# modellist = []

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

def upload_file_handler(instance, filename):
    return os.path.join('TrainModel', filename)

class DetectorModel(models.Model):
    name = models.CharField(max_length=256, unique=True)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    # feature_extractor_type = models.CharField(max_length=256, default="", blank=False)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    file = models.FileField(upload_to=upload_file_handler)

    logger.info(owner)
    # logger.info(name)
    # logger.info(self.file.name)
    # temp = provider.DetectorSelfModel(name, file.name, feature_extractor_type)
    # configFile = models.FileField(upload_to=upload_file_handler, storage=FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT)))
    # upload_to="background/"

    class Meta:
        ordering = ['id']

    def __init__(self, *args, **kwargs):
        super(DetectorModel, self).__init__(*args, **kwargs)
        logger.info(self.name)
        # logger.info(self.feature_extractor_type)
        logger.info(self.getId())
        logger.info(self.getFileName())
        logger.info(self.getPath())

    def save(self, *args, **kwargs):
        super(DetectorModel, self).save(*args, **kwargs)
        logger.info("able to get here")
        # savingpath = os.path.abspath(self.file.name)
        # logger.info(self.file.path)
        # str(pathlib.Path(settings.VAR_DIR)) + '/TrainModel/' + self.file.name
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(Zip2Model, self.file.path, self.name)
            self.unzipresult = future.result()
            # unzipprocess = threading.Thread(target=Zip2Model, args=(self.file.path, self.name,))
            # unzipprocess.start()
        
        logger.info("after thread")
    
    def getPath(self):
        return os.path.join(settings.TRAINMODEL_ROOT, self.name)

    def getUnzip(self):
        return self.unzipresult

    def getFilePath(self):
        return self.unzipprocess.file

    def getFileName(self):
        return self.file.name

    def __str__(self):
        return self.name

    def getId(self):
        return self.id

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

    # def get_pretrain_dir(self):
    #     return self.get_dir() / 'pretrain'

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
