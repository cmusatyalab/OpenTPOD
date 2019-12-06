"""Background tasks for object_detector
"""
import json
import os
import pathlib
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import traceback
from ast import literal_eval
from datetime import datetime
from distutils.dir_util import copy_tree
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest

import django_rq
import psutil
import rq
from django.conf import settings
from django.db import transaction
from logzero import logger
from PIL import Image

from . import datasets, models, provider


def _train(db_detector,
           db_tasks,
           db_user,
           scheme,
           host):
    # dump annotations
    datasets.dump_detector_annotations(db_detector,
                                       db_tasks,
                                       db_user,
                                       scheme,
                                       host)
    # refresh db_detector object to make sure it is fresh
    db_detector = models.Detector.objects.get(id=db_detector.id)
    detector = db_detector.get_detector_object()
    db_detector.status = str(models.Status.TRAINING)
    db_detector.save()

    try:
        detector.prepare()
        detector.train()

        # refresh db obj as a long time has passed after training
        db_detector = models.Detector.objects.get(id=db_detector.id)
        db_detector.status = str(models.Status.TRAINED)
    except Exception as e:
        logger.error('ERROR: Training failed.')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(''.join(traceback.format_exception(
            exc_type, exc_value,
            exc_traceback)))
        db_detector.status = str(models.Status.ERRORED)
    finally:
        db_detector.save()


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
            db_detector.train_set.tasks.all(),
            db_user,
            scheme,
            host),
    )


def _visualize_tensorboard(model_dir, pid_file_path):
    from tensorboard import program
    with open(pid_file_path, 'w') as f:
        f.write(json.dumps(os.getpid()))
    tb = program.TensorBoard()
    tb.configure(argv=[
        None, '--logdir', model_dir,
        '--host', settings.TENSORBOARD_HOST, '--port', settings.TENSORBOARD_PORT])
    url = tb.launch()
    while True:
        time.sleep(1000)


def _find_open_port():
    """Use socket's built in ability to find an open port."""
    sock = socket.socket()
    sock.bind(('', 0))
    _, port = sock.getsockname()
    sock.close()
    return port


def _visualize_tensorboard_subprocess(model_dir, pid_file_path):
    # tensorboard will automatically find an available port to open
    port = _find_open_port()
    cmd = ('tensorboard ' +
           '--logdir={} '.format(model_dir) +
           '--host={} '.format(settings.TENSORBOARD_HOST) +
           '--port={}'.format(port))
    logger.info('\n===========================================\n')
    logger.info('\n\tStarting Tensorboard with following command: \n\n{}'.format(cmd))
    logger.info('\n===========================================\n')
    process = subprocess.Popen(
        cmd.split())
    with open(pid_file_path, 'w') as f:
        f.write(json.dumps({'pid': process.pid, 'port': port}))


def visualize(db_detector):
    """Visualize detector training procedures.

    Currently only supports tensorboard. However, due to tensorboard spawns a
    separate process to run. We're writing it's worker horse process pid to a
    file. When another visualization request comes, we'll first check if a
    tensorboard worker horse process is running. If so, that process is killed.

    Once tensorboard is up, we use django-revproxy to proxy requests to that
    local tensorboard server.

    However, this only supports 1 tensorboard running across all users...
    Need to find a better way...
    """
    # TODO(junjuew): check celery to see if there are more elegant methods
    # of killing a launched task. Somehow, celery is not showing the long-running
    # _visualize_tensorboard job as active, only as registerd..
    # kill running tb process if there is one
    pid_file_path = (db_detector.get_model_dir() / 'tensorboard.pinfo').resolve()
    if pid_file_path.exists():
        with open(pid_file_path, 'r') as f:
            subprocess_info = json.loads(f.read())
            pid = subprocess_info['pid']
            port = subprocess_info['port']
            p = psutil.Process(pid)

            for connection in p.connections():
                if connection.laddr[1] == port:
                    # if the process is still running
                    # no need to launch a new process
                    if connection.status == psutil.CONN_LISTEN:
                        return
                    else:
                        # the process is somehow no longer listening on it
                        # try kill it
                        try:
                            os.kill(pid, signal.SIGKILL)
                        except ProcessLookupError as e:
                            pass

    queue = django_rq.get_queue('tensorboard')
    rq_job = queue.enqueue_call(
        func=_visualize_tensorboard_subprocess,
        args=(str(db_detector.get_model_dir()), str(pid_file_path),),
        result_ttl=86400  # result expires after 1 day
    )
