"""Background tasks for object_detector
"""
import os
from datetime import datetime
import shutil
import sys
from ast import literal_eval
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

from . import models
from cvat.apps.engine import annotation as cvat_annotation
from cvat.apps.annotation import models as cvat_models


def prepare_data(trainset, user,
                 scheme, host):
    """Dump data from CVAT DB to on-disk format
    """
    queue = django_rq.get_queue('default')
    # another type is: TFRECORD ZIP 1.0
    dump_format = 'COCO JSON 1.0'

    db_dumper = cvat_models.AnnotationDumper.objects.get(
        display_name=dump_format)
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

    for video in trainset.videos.all():
        task = video.task
        output_file_path = os.path.join(task.get_task_dirname(),
                                        '{}.{}.{}.{}'.format(task.name,
                                                             user.username,
                                                             timestamp, db_dumper.format.lower()))
        rq_id = '{}@/api/v1/tasks/{}/annotations/{}'.format(user.username,
                                                            task.id,
                                                            output_file_path)
        rq_job = queue.enqueue_call(
            func=cvat_annotation.dump_task_data,
            args=(task.id, user, output_file_path, db_dumper,
                  scheme, host),
            job_id=rq_id,
        )
        rq_job.meta['file_path'] = output_file_path
        rq_job.save_meta()


def train():
    pass
