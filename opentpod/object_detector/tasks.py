"""Background tasks for object_detector
"""
import json
import os
import pathlib
import re
import shutil
import signal
import sys
import time
from ast import literal_eval
from datetime import datetime
from distutils.dir_util import copy_tree
from traceback import print_exception
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest

import django_rq
import rq
from celery.decorators import task
from celery.task import control
from django.conf import settings
from django.db import transaction
from PIL import Image

from . import datasets, models, provider


def _train(db_detector,
           db_user,
           scheme,
           host):

    # dump annotations
    datasets.dump_detector_annotations(db_detector, db_user, scheme, host)
    detector = db_detector.get_detector_object()
    # detector_class = provider.get(db_detector.dnn_type)
    # config = db_detector.get_train_config()
    # config['input_dir'] = db_detector.get_training_data_dir().resolve()
    # config['output_dir'] = db_detector.get_model_dir().resolve()
    # detector = detector_class(config)
    detector.prepare()
    detector.train()


def export(db_detector):
    detector = db_detector.get_detector_object()
    detector.export(db_detector.get_export_file_path())


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

@task
def visualize_tensorboard(model_dir):
    from tensorboard import program
    with open(settings.CACHE_DIR / 'tensorboard.pid', 'w') as f:
        f.write(json.dumps(os.getpid()))
    tb = program.TensorBoard()
    tb.configure(argv=[
        None, '--logdir', model_dir,
        '--host', settings.TENSORBOARD_HOST, '--port', settings.TENSORBOARD_PORT])
    url = tb.launch()
    while True:
        time.sleep(1000)

def visualize(db_detector):
    # TODO(junjuew): check celery to see if there are more elegant methods
    # this method only allows 1 tensorboard session to be open
    # among all users ...
    with open(settings.CACHE_DIR / 'tensorboard.pid', 'r') as f:
        pid = json.loads(f.read())
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError as e:
            pass
    visualize_tensorboard.apply_async(
        args = (str(db_detector.get_model_dir()),),
        task_id='tb')
    # queue = django_rq.get_queue('tensorboard')
    # rq_job = queue.enqueue_call(
    #     func=_visualize_tensorboard,
    #     args=(
    #         str(db_detector.get_model_dir()),
    #         )
    # )
