"""Tensorflow Object Detection API provider
"""
from urllib import request
import shutil
import zipfile
import pathlib
import subprocess

# from django.conf import settings
from mako import template
from logzero import logger

import object_detection


class TFODDetector():
    """Tensorflow Object Detection API
    See: https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/running_locally.md
    """

    def __init__(self, train_dir, model_dir, config):
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
        self._train_dir = train_dir
        self._train_config_file_path = self._train_dir.resolve() / 'pipeline.config'
        self._model_dir = model_dir
        self._config = config
        # TODO (junjuew): move to datasets.py?
        self._config['train_input_path'] = str(self._train_dir.resolve() / 'train.tfrecord')
        self._config['eval_input_path'] = str(self._train_dir.resolve() / 'eval.tfrecord')
        self._config['label_map_path'] = str(self._train_dir.resolve() / 'label_map.pbtxt')
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
        parent_model_dir = self._config['fine_tune_checkpoint']
        if parent_model_dir in self.PRETRAIN_MODEL_URLS:
            model_cache_dir = self._cache_dir / parent_model_dir
            if not model_cache_dir.exists():
                self._download_and_extract_pretrained_model(parent_model_dir,
                                                            model_cache_dir)
            potential_pretained_model_files = list(model_cache_dir.glob('**/model.ckpt*'))
            if len(potential_pretained_model_files) == 0:
                raise ValueError('Failed to find pretrained model in {}'.format(model_cache_dir))
            fine_tune_model_dir = potential_pretained_model_files[0].parent
            self._config['fine_tune_checkpoint'] = str(fine_tune_model_dir.resolve() / 'model.ckpt')

    def _prepare_config_pipeline_file(self):
        # TODO(junjuew): need to choose the correct config by dnn type
        pipeline_config = template.Template(self.FASTER_RCNN_RESNET101_CONFIG).render(
            num_classes=self._config['num_classes'],
            fine_tune_checkpoint=self._config['fine_tune_checkpoint'],
            batch_size=self._config['batch_size'],
            num_steps=self._config['num_steps'],
            train_input_path=self._config['train_input_path'],
            eval_input_path=self._config['eval_input_path'],
            label_map_path=self._config['label_map_path']
        )
        with open(self._train_config_file_path, 'w') as f:
            f.write(pipeline_config)

    def prepare(self):
        self._prepare_parent_model_dir()
        self._prepare_config_pipeline_file()

    def train(self):
        train_cmd = 'python -m object_detection.model_main --pipeline_config_path {0} --model_dir {1} --alsologtostderr > {1}/train.log 2>&1'.format(
            self._train_config_file_path,
            self._model_dir
        )
        logger.info('launching training process with following command: \n\n{}'.format(train_cmd))
        process = subprocess.Popen(
            train_cmd.split())

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
    num_classes: ${num_classes}
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
batch_size: ${batch_size}
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
fine_tune_checkpoint: "${fine_tune_checkpoint}"
from_detection_checkpoint: true
load_all_detection_checkpoint_vars: true
# Note: The below line limits the training process to 200K steps, which we
# empirically found to be sufficient enough to train the pets dataset. This
# effectively bypasses the learning rate schedule (the learning rate will
# never decay). Remove the below line to train indefinitely.
num_steps: ${num_steps}
data_augmentation_options {
    random_horizontal_flip {
    }
}
}

train_input_reader: {
tf_record_input_reader {
    input_path: "${train_input_path}"
}
label_map_path: "${label_map_path}"
}

eval_config: {
metrics_set: "coco_detection_metrics"
num_examples: 1101
}

eval_input_reader: {
tf_record_input_reader {
    input_path: "${eval_input_path}"
}
label_map_path: "${label_map_path}"
shuffle: true
num_readers: 1
}
"""


if __name__ == "__main__":
    dt = TFODDetector(
        data_dir='', parent_model_dir='faster_rcnn_resnet101'
    )
    dt.prepare()
