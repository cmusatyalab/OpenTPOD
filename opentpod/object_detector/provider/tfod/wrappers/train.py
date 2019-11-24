"""Wrapper Script to call tf object detection API's continuous train and eval.

Eval is run after every checkpoint. The frequency of checkpoint is determined by
RunConfig arguments save_checkpoints_steps or save_checkpoints_secs (default:
600s). However, current tf object detection API doens't provide an easy method
to override RunConfig. See: https://github.com/tensorflow/models/issues/5246
"""
import os
import sys
import pathlib
import json

from absl import flags
import tensorflow as tf
from object_detection import model_main

FLAGS = flags.FLAGS


def _check_training_data_dir():
    """Check training directory's data is valid

    Fail if missing files, or # of training/eval examples used is not positive
    """
    training_data_dir = pathlib.Path(FLAGS.pipeline_config_path).parent
    assert (training_data_dir / 'meta').resolve().exists()
    assert (training_data_dir / 'label_map.pbtxt').resolve().exists()
    assert (training_data_dir / 'label_map.pbtxt').resolve().stat().st_size > 0
    assert (training_data_dir / 'train.tfrecord').resolve().exists()
    with open(training_data_dir / 'meta', 'r') as f:
        meta = json.load(f)
        assert(meta["train_num"] > 0)
        assert(meta["eval_num"] > 0)


def main(unused):
    from opentpod.object_detector import provider
    output_dir = FLAGS.model_dir
    # redirect logging to file
    sys.stderr = open(os.path.join(output_dir, 'train.log'), "w")
    status_file_path = pathlib.Path(output_dir) / 'status'
    _check_training_data_dir()
    with open(status_file_path, "w") as f:
        f.write(provider.Status.TRAINING.value)
    try:
        model_main.main(unused)
        with open(status_file_path, "w") as f:
            f.write(provider.Status.TRAINED.value)
    except:
        import pdb
        pdb.set_trace()
        with open(status_file_path, "w") as f:
            f.write(provider.Status.ERROR.value)
    finally:
        sys.stderr.flush()
        sys.stderr.close()


if __name__ == '__main__':
    tf.app.run()
