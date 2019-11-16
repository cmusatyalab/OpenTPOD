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
from cvat.apps.engine import annotation as cvat_annotation
from django.conf import settings
from django.db import transaction
from PIL import Image

from . import models


def dump_task_image_and_annotation(
        detector_dir,
        detector_training_data_dir,
        task_id,
        task_data_dir,
        user,
        annotation_file_path,
        db_dumper,
        scheme,
        host):
    """Dump data for a task. Put the end result to detector's directory
    """
    detector_dir = pathlib.Path(detector_dir)
    cvat_annotation.dump_task_data(
        task_id, user, annotation_file_path, db_dumper, scheme, host)
    detector_annotation_file_path = detector_dir / os.path.basename(annotation_file_path)
    shutil.move(annotation_file_path, detector_annotation_file_path)

    prepare_coco_dataset(
        detector_annotation_file_path,
        task_data_dir,
        detector_training_data_dir
    )


def _cvat_get_frame_path(base_dir, frame):
    """CVAT's image directory layout.

    Specified in cvat.engine.models.py Task class
    """
    d1 = str(int(frame) // 10000)
    d2 = str(int(frame) // 100)
    path = os.path.join(base_dir, d1, d2,
                        str(frame) + '.jpg')

    return path


def prepare_coco_dataset(annotation_file_path, cvat_image_dir, output_dir):
    """Create a on-disk coco dataset with both images and annotations.
    """
    from pycocotools import coco as coco_loader

    annotation_file_path = pathlib.Path(annotation_file_path).resolve()
    output_dir = pathlib.Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # annotation file
    annotation_file_name = 'annotation.json'
    os.symlink(annotation_file_path, output_dir / annotation_file_name)

    # image files
    output_data_dir = output_dir / 'images'
    shutil.rmtree(output_data_dir, ignore_errors=True)
    output_data_dir.mkdir()
    coco_dataset = coco_loader.COCO(str(annotation_file_path))
    coco_images = coco_dataset.loadImgs(coco_dataset.getImgIds())
    cvat_frame_id_regex = re.compile(r'\d+')
    for coco_image in coco_images:
        coco_file_name = coco_image['file_name']
        # cvat uses "frame_{:06d}".format(frame) as default file name
        # see cvat.annotations.annotation
        cvat_frame_id = int(cvat_frame_id_regex.findall(coco_file_name)[0])
        input_image_file_path = _cvat_get_frame_path(cvat_image_dir,
                                                     cvat_frame_id)
        output_image_file_path = output_data_dir / coco_file_name
        os.symlink(input_image_file_path, output_image_file_path)


def prepare_data(db_detector,
                 db_trainset,
                 user,
                 scheme,
                 host):
    """Dump data from CVAT DB to on-disk format
    """
    queue = django_rq.get_queue('default')
    # another type is: TFRECORD ZIP 1.0
    dump_format = 'COCO JSON 1.0'

    db_dumper = cvat_models.AnnotationDumper.objects.get(
        display_name=dump_format)
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

    # TODO(junjuew): need to merge all tasks into a single dataset
    # checkout coco assistant: https://github.com/ashnair1/COCO-Assistant

    for video in db_trainset.videos.all():
        task = video.task
        output_file_path = os.path.join(task.get_task_dirname(),
                                        '{}.{}.{}.{}'.format(task.name,
                                                             user.username,
                                                             timestamp, db_dumper.format.lower()))
        rq_id = '{}@/api/v1/tasks/{}/annotations/{}'.format(user.username,
                                                            task.id,
                                                            output_file_path)
        rq_job = queue.enqueue_call(
            func=dump_task_image_and_annotation,
            args=(
                db_detector.get_dir(),
                db_detector.get_training_data_dir(),
                task.id,
                task.get_data_dirname(),
                user,
                output_file_path,
                db_dumper,
                scheme,
                host),
            job_id=rq_id,
        )
        rq_job.meta['file_path'] = output_file_path
        rq_job.save_meta()


def train():
    pass
