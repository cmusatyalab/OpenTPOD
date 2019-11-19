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
from cvat.apps.annotation import models as cvat_models
from django.conf import settings
from django.db import transaction
from PIL import Image

from . import models, datasets


def prepare_data(db_detector,
                 db_trainset,
                 db_user,
                 scheme,
                 host):
    """Dump data from CVAT DB to on-disk format
    """
    queue = django_rq.get_queue('default')
    # another type is: TFRecord ZIP 1.0, see cvat.apps.annotation
    # dump_format = 'COCO JSON 1.0'
    dump_format = 'TFRecord ZIP 1.0'
    db_dumper = cvat_models.AnnotationDumper.objects.get(
        display_name=dump_format)

    # TODO(junjuew): need to merge all tasks into a single dataset
    rq_job = queue.enqueue_call(
        func=datasets.dump_detector_annotations,
        args=(
            db_detector,
            db_user,
            db_dumper,
            scheme,
            host),
    )
    # rq_job.meta['file_path'] = output_file_path
    # rq_job.save_meta()
    # for db_video in db_trainset.videos.all():


def train():
    pass
