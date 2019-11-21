import os
import sys
import pathlib

from absl import flags
from object_detection import model_main
from opentpod.object_detector import models

import tensorflow as tf

FLAGS = flags.FLAGS


def main(unused):
    output_dir = FLAGS.model_dir
    status_file_path = pathlib.Path(output_dir) / 'status'
    # redirect logging to file
    sys.stderr = open(os.path.join(output_dir, 'train.log'), "w")
    with open(status_file_path, "w") as f:
        f.write(models.Status.TRAINING.value)
    try:
        model_main.main(unused)
        with open(status_file_path, "w") as f:
            f.write(models.Status.TRAINED.value)
    except:
        with open(status_file_path, "w") as f:
            f.write(models.Status.ERROR.value)
    finally:
        sys.stderr.flush()
        sys.stderr.close()


if __name__ == '__main__':
    tf.app.run()
