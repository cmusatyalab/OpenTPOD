from .tfod import TFODFasterRCNNResNet101, TFODFasterRCNNResNet50, TFODSSDMobileNetV2

SUPPORTED_DNN_TYPE = [
    # class name, db type name, human readable name
    (TFODFasterRCNNResNet101, 'tensorflow_faster_rcnn_resnet101', 'Tensorflow Faster-RCNN ResNet 101'),
    (TFODFasterRCNNResNet50, 'tensorflow_faster_rcnn_resnet50', 'Tensorflow Faster-RCNN ResNet 50'),
    (TFODSSDMobileNetV2, 'tensorflow_ssd_mobilenet_v2', 'Tensorflow SSD MobileNet V2'),
]
# dnn type string to use for db and human readable text
DNN_TYPE_DB_CHOICES = [
    (dnn_info[1], dnn_info[2])
    for dnn_info in SUPPORTED_DNN_TYPE
]

DNN_TYPE_TO_CLASS = {
    dnn_info[1]: dnn_info[0] for dnn_info in SUPPORTED_DNN_TYPE
}


def get(dnn_type):
    return DNN_TYPE_TO_CLASS[dnn_type]
