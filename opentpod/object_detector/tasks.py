"""Background tasks for object_detector
"""
import os
import re
import pathlib
import shutil
import sys
from ast import literal_eval
from datetime import datetime
from distutils.dir_util import copy_tree
from traceback import print_exception
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest

import django_rq
import rq
from django.conf import settings
from django.db import transaction
from PIL import Image

from . import models, datasets, provider


def _train(db_detector,
           db_user,
           scheme,
           host):

    # dump annotations
    datasets.dump_detector_annotations(db_detector, db_user, scheme, host)
    detector_class = provider.get(db_detector.dnn_type)
    # launch training
    config = db_detector.get_train_config()
    config['input_dir'] = db_detector.get_training_data_dir().resolve()
    config['output_dir'] = db_detector.get_model_dir().resolve()
    detector = detector_class(config)
    detector.prepare()
    detector.train()


def train(db_detector,
          db_user,
          scheme,
          host):
    """Dump data from CVAT DB to on-disk format
    """
    queue = django_rq.get_queue('low')
    rq_job = queue.enqueue_call(
        func=_train,
        args=(
            db_detector,
            db_user,
            scheme,
            host),
    )
    # rq_job.meta['file_path'] = output_file_path
    # rq_job.save_meta()
