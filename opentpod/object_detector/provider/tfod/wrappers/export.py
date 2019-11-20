# INPUT_TYPE=image_tensor
# PIPELINE_CONFIG_PATH={path to pipeline config file}
# TRAINED_CKPT_PREFIX={path to model.ckpt}
# EXPORT_DIR={path to folder that will be used for export}
# python object_detection/export_inference_graph.py \
#     --input_type=${INPUT_TYPE} \
#     --pipeline_config_path=${PIPELINE_CONFIG_PATH} \
#     --trained_checkpoint_prefix=${TRAINED_CKPT_PREFIX} \
#     --output_directory=${EXPORT_DIR}
"""Thin wrapper script to run TF export script in a subprocess
"""
from absl import flags
from object_detection import export_inference_graph

import tensorflow as tf

FLAGS = flags.FLAGS


def main(unused):
    export_inference_graph.main(unused)


if __name__ == '__main__':
    tf.app.run()
