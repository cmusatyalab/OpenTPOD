from .tfod import TFODFasterRCNNResNet101, TFODFasterRCNNResNet50, TFODSSDMobileNetV2, DetectorSelfModel

from enum import Enum

from .tfod.base import TFODDetector

from django.conf import settings

from logzero import logger
import os
import zipfile

class Status(Enum):
    CREATED = 'created'
    TRAINING = 'training'
    TRAINED = 'trained'
    ERROR = 'error'

    @classmethod
    def choices(self):
        return tuple((x.value, x.name) for x in self)

    def __str__(self):
        return self.value



# SELFMODELPATH = os.path.join(settings.TRAINMODEL_ROOT, 'modelpath')
# SELFMODEL = ""

# if os.path.exists(SELFMODELPATH):
#     premodel = open(SELFMODELPATH, 'r')
#     SELFMODEL = premodel.read()
#     premodel.close()

# CONFIGPATH = os.path.join(SELFMODEL, 'pipeline.config')
# TEMPLATE = ""
# if os.path.exists(CONFIGPATH):
#     f = open(CONFIGPATH, 'r')
#     TEMPLATE = f.read()
#     logger.info('update TEMPLATE')
#     f.close()

# content = f.read()
# logger.info(content)
# logger.info(CONFIGPATH)

# logger.info("trying to test changing")
# logger.info(type(TEMPLATE))

# class DetectorSelfModel(TFODDetector):
#     TRAINING_PARAMETERS = {'batch_size': 2, 'num_steps': 20000}

#     def __init__(self, config):
#         super().__init__(config)
#         logger.info('init in self model')

#     @property
#     def pretrained_model_url(self):
#         logger.info('get url')
#         return SELFMODEL

#     @property
#     def pipeline_config_template(self):
#         return TEMPLATE

_SUPPORTED_DNN_TYPE = [
    # class name, db type name, human readable name
    (TFODFasterRCNNResNet101, 'tensorflow_faster_rcnn_resnet101', 'Tensorflow Faster-RCNN ResNet 101'),
    (TFODFasterRCNNResNet50, 'tensorflow_faster_rcnn_resnet50', 'Tensorflow Faster-RCNN ResNet 50'),
    (TFODSSDMobileNetV2, 'tensorflow_ssd_mobilenet_v2', 'Tensorflow SSD MobileNet V2'),
    (DetectorSelfModel, 'Self-trained', 'Self-trained'),
]

# dnn type string to use for db and human readable text
DNN_TYPE_DB_CHOICES = [
    (dnn_info[1], dnn_info[2])
    for dnn_info in _SUPPORTED_DNN_TYPE
]

DNN_TYPE_TO_CLASS = {
    dnn_info[1]: dnn_info[0] for dnn_info in _SUPPORTED_DNN_TYPE
}


def get(dnn_type, default=None):
    if dnn_type in DNN_TYPE_TO_CLASS:
        return DNN_TYPE_TO_CLASS[dnn_type]
    return default
