"""Tensorflow Object Detection API provider
"""
from urllib import request
import shutil
import zipfile
import pathlib

# from django.conf import settings
from logzero import logger


class TFODDetector():
    """Tensorflow Object Detection API
    See: https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/running_locally.md
    """

    def __init__(self, data_dir, parent_model_dir):
        """Expected directory layout
            +data
                -label_map file
                -train TFRecord file
                -eval TFRecord file
            +models
                + model
                    -pipeline config file
                    +train
                    +eval
        Arguments:
            data_dir {[type]} -- [description]
            parent_model_dir {[type]} -- [description]
        """
        super().__init__()
        self._data_dir = data_dir
        self._parent_model_dir = parent_model_dir
        # self._cache_dir = settings.DATA_ROOT / '.cache'
        self._cache_dir = pathlib.Path('.cache')
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _download_and_extract_pretrained_model(self, model_name, output_dir):
        logger.info('downloading and caching pretrained {} from tensorflow website'.format(
            model_name))
        model_url = self.PRETRAIN_MODEL_URLS[model_name]
        output_dir.mkdir(parents=True, exist_ok=True)
        model_file_basename = model_url.split('/')[-1]
        download_to_file_path = self._cache_dir / model_file_basename
        with request.urlopen(model_url) as response, open(download_to_file_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        shutil.unpack_archive(download_to_file_path, output_dir)
        logger.info('downloading --> {} finished.'.format(output_dir))

    def _prepare_parent_model_dir(self):
        if self._parent_model_dir in self.PRETRAIN_MODEL_URLS:
            model_cache_dir = self._cache_dir / self._parent_model_dir
            if not model_cache_dir.exists():
                self._download_and_extract_pretrained_model(self._parent_model_dir,
                                                            model_cache_dir)

    def prepare(self):
        self._prepare_parent_model_dir()

    def load(self):
        pass

    def train(self):
        pass

    def run(self):
        pass

    PRETRAIN_MODEL_URLS = {
        'faster_rcnn_resnet101': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet101_coco_2018_01_28.tar.gz',
        'ssd_mobilenet_v2': 'http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz'
    }

    FASTER_RCNN_RESNET101_CONFIG = """
    # Faster R-CNN with Resnet-101 (v1) configured for the Oxford-IIIT Pet Dataset.
    # Users should configure the fine_tune_checkpoint field in the train config as
    # well as the label_map_path and input_path fields in the train_input_reader and
    # eval_input_reader. Search for "PATH_TO_BE_CONFIGURED" to find the fields that
    # should be configured.

    model {
    faster_rcnn {
        num_classes: 37
        image_resizer {
        keep_aspect_ratio_resizer {
            min_dimension: 600
            max_dimension: 1024
        }
        }
        feature_extractor {
        type: 'faster_rcnn_resnet101'
        first_stage_features_stride: 16
        }
        first_stage_anchor_generator {
        grid_anchor_generator {
            scales: [0.25, 0.5, 1.0, 2.0]
            aspect_ratios: [0.5, 1.0, 2.0]
            height_stride: 16
            width_stride: 16
        }
        }
        first_stage_box_predictor_conv_hyperparams {
        op: CONV
        regularizer {
            l2_regularizer {
            weight: 0.0
            }
        }
        initializer {
            truncated_normal_initializer {
            stddev: 0.01
            }
        }
        }
        first_stage_nms_score_threshold: 0.0
        first_stage_nms_iou_threshold: 0.7
        first_stage_max_proposals: 300
        first_stage_localization_loss_weight: 2.0
        first_stage_objectness_loss_weight: 1.0
        initial_crop_size: 14
        maxpool_kernel_size: 2
        maxpool_stride: 2
        second_stage_box_predictor {
        mask_rcnn_box_predictor {
            use_dropout: false
            dropout_keep_probability: 1.0
            fc_hyperparams {
            op: FC
            regularizer {
                l2_regularizer {
                weight: 0.0
                }
            }
            initializer {
                variance_scaling_initializer {
                factor: 1.0
                uniform: true
                mode: FAN_AVG
                }
            }
            }
        }
        }
        second_stage_post_processing {
        batch_non_max_suppression {
            score_threshold: 0.0
            iou_threshold: 0.6
            max_detections_per_class: 100
            max_total_detections: 300
        }
        score_converter: SOFTMAX
        }
        second_stage_localization_loss_weight: 2.0
        second_stage_classification_loss_weight: 1.0
    }
    }

    train_config: {
    batch_size: 1
    optimizer {
        momentum_optimizer: {
        learning_rate: {
            manual_step_learning_rate {
            initial_learning_rate: 0.0003
            schedule {
                step: 900000
                learning_rate: .00003
            }
            schedule {
                step: 1200000
                learning_rate: .000003
            }
            }
        }
        momentum_optimizer_value: 0.9
        }
        use_moving_average: false
    }
    gradient_clipping_by_norm: 10.0
    fine_tune_checkpoint: "PATH_TO_BE_CONFIGURED/model.ckpt"
    from_detection_checkpoint: true
    load_all_detection_checkpoint_vars: true
    # Note: The below line limits the training process to 200K steps, which we
    # empirically found to be sufficient enough to train the pets dataset. This
    # effectively bypasses the learning rate schedule (the learning rate will
    # never decay). Remove the below line to train indefinitely.
    num_steps: 200000
    data_augmentation_options {
        random_horizontal_flip {
        }
    }
    }

    train_input_reader: {
    tf_record_input_reader {
        input_path: "PATH_TO_BE_CONFIGURED/pet_faces_train.record-?????-of-00010"
    }
    label_map_path: "PATH_TO_BE_CONFIGURED/pet_label_map.pbtxt"
    }

    eval_config: {
    metrics_set: "coco_detection_metrics"
    num_examples: 1101
    }

    eval_input_reader: {
    tf_record_input_reader {
        input_path: "PATH_TO_BE_CONFIGURED/pet_faces_val.record-?????-of-00010"
    }
    label_map_path: "PATH_TO_BE_CONFIGURED/pet_label_map.pbtxt"
    shuffle: false
    num_readers: 1
    }
    """


if __name__ == "__main__":
    dt = TFODDetector(
        data_dir='', parent_model_dir='faster_rcnn_resnet101'
    )
    dt.prepare()
