import os
import sys
import pathlib

from absl import flags
from object_detection import model_main

import tensorflow as tf

FLAGS = flags.FLAGS


def main(unused):
    output_dir = FLAGS.model_dir
    status_file_path = pathlib.Path(output_dir) / 'status'
    # redirect logging to file
    sys.stderr = open(os.path.join(output_dir, 'train.log'), "w")
    with open(status_file_path, "w") as f:
        f.write('training')
    try:
        model_main.main(unused)
        with open(status_file_path, "w") as f:
            f.write('trained')
    except:
        with open(status_file_path, "w") as f:
            f.write('error')
    finally:
        sys.stderr.flush()
        sys.stderr.close()


if __name__ == '__main__':
    tf.app.run()
