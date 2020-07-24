from .tfod import TFODFasterRCNNResNet101, TFODFasterRCNNResNet50, TFODSSDMobileNetV2, DetectorSelfModel, DetectorGoogleAutoML

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

_SUPPORTED_DNN_TYPE = [
    # class name, db type name, human readable name
    (TFODFasterRCNNResNet101, 'tensorflow_faster_rcnn_resnet101', 'Tensorflow Faster-RCNN ResNet 101'),
    (TFODFasterRCNNResNet50, 'tensorflow_faster_rcnn_resnet50', 'Tensorflow Faster-RCNN ResNet 50'),
    (TFODSSDMobileNetV2, 'tensorflow_ssd_mobilenet_v2', 'Tensorflow SSD MobileNet V2'),
    (DetectorSelfModel, 'Self-trained', 'Self-trained'),
    (DetectorGoogleAutoML, 'GoogleAutoML', 'GoogleAutoML'),
]

# dnn type string to use for db and human readable text
DNN_TYPE_DB_CHOICES = [
    (dnn_info[1], dnn_info[2])
    for dnn_info in _SUPPORTED_DNN_TYPE
]

# def getDB(id):
#     logger.info('this is a test')
#     logger.info(id)
#     choices = []
#     for i in _SUPPORTED_DNN_TYPE:
#         logger.info(i[2])
#         if i[2] == 'Self-trained':
#             path = os.path.join(settings.TRAINMODEL_ROOT, str(id), 'modelpath')
#             logger.info(path)
#             if os.path.exists(path):
#                 fp = open(path, 'r')
#                 content = fp.read()
#                 logger.info(content)
#                 if os.path.exists(content):
#                     name = path[len(str(os.path.join(settings.TRAINMODELs_ROOT, str(id) + 1))):]
#                     logger.info(name)
#                     choices.append((i[1], i[2] + ' - ' + name))
#         else:
#             logger.info('this is not ' + i[2])
#             # logger.info(i[2])
#             choices.append((i[1], i[2]))

#     return choices


DNN_TYPE_TO_CLASS = {
    dnn_info[1]: dnn_info[0] for dnn_info in _SUPPORTED_DNN_TYPE
}

def get(dnn_type, default=None):
    if dnn_type in DNN_TYPE_TO_CLASS:
        return DNN_TYPE_TO_CLASS[dnn_type]
    return default
