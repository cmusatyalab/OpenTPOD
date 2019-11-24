from .tfod import TFODFasterRCNNResNet101, TFODFasterRCNNResNet50, TFODSSDMobileNetV2

from enum import Enum


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
