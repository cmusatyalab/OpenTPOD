"""Dataset functions.
"""
import os
import pathlib
import re
import tempfile
from datetime import datetime
from zipfile import ZipFile

import tensorflow as tf
import numpy as np

from cvat.apps.engine import annotation as cvat_annotation
import collections
import json


def _cvat_get_frame_path(base_dir, frame):
    """CVAT's image directory layout.

    Specified in cvat.engine.models.py Task class
    """
    d1 = str(int(frame) // 10000)
    d2 = str(int(frame) // 100)
    path = os.path.join(base_dir, d1, d2,
                        str(frame) + '.jpg')

    return path


def dump_cvat_task_annotations(
        db_task,
        db_user,
        db_dumper,
        scheme,
        host):
    """Use CVAT's utilities to dump annotations for a task."""
    task_id = db_task.id
    task_image_dir = db_task.get_data_dirname()
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    output_file_path = os.path.join(db_task.get_task_dirname(),
                                    '{}.{}.{}.{}'.format(db_task.id,
                                                         db_user.username,
                                                         timestamp,
                                                         db_dumper.format.lower()))
    cvat_annotation.dump_task_data(
        task_id, db_user, output_file_path, db_dumper, scheme, host)
    return output_file_path


def _add_image_data_to_cvat_tfexample(tfexample, cvat_image_dir):
    image_file_name = tfexample.features.feature['image/filename'].bytes_list.value[0].decode('utf-8')
    cvat_frame_id = int(re.findall(r'\d+', image_file_name)[0])
    with open(_cvat_get_frame_path(cvat_image_dir, cvat_frame_id), 'rb') as f:
        frame_data = f.read()
        tfexample.features.feature['image/encoded'].bytes_list.value.append(frame_data)


def add_image_to_cvat_tfrecord(cvat_image_dir, cvat_tf_record_zip, output_file_path):
    """Add image data to cvat tfrecord."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with ZipFile(cvat_tf_record_zip) as cur_zip:
            cur_zip.extractall(temp_dir)
        tfrecord_files = list(pathlib.Path(temp_dir).glob('*.tfrecord'))
        tfrecord_files = [str(tfrecord_file) for tfrecord_file in tfrecord_files]
        dataset = tf.data.TFRecordDataset(tfrecord_files)
        with tf.io.TFRecordWriter(str(output_file_path)) as writer:
            for item in iter(dataset):
                example = tf.train.Example()
                example.ParseFromString(item.numpy())
                _add_image_data_to_cvat_tfexample(example, cvat_image_dir)
                writer.write(example.SerializeToString())


def get_label_map_from_cvat_tfrecord_zip(cvat_tf_record_zip):
    """Extract label map from cvat tfrecord zip file.
    CVAT's tfrecord file contains:
    - label_map.pbtxt
    - *.tfrecord
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with ZipFile(cvat_tf_record_zip) as cur_zip:
            with cur_zip.open('label_map.pbtxt', 'r') as f:
                content = f.read().decode('utf-8')
                labels = re.findall(r"\tname: '(\w+)'\n", content)
                return labels


def dump_metadata(metadata, output_file_path):
    with open(output_file_path, 'w') as f:
        json.dump(metadata, f)


def _dump_labelmap_file(labels, output_file_path):
    """Write out labels as tensorflow object detection API's lable_map.txt.
    https://github.com/tensorflow/models/blob/master/research/object_detection/data/kitti_label_map.pbtxt

    Label id 0 is reserved for 'background', therefore this file starts with id 1.
    """
    label_ids = collections.OrderedDict((label, idx + 1)
                                        for idx, label in enumerate(labels))
    with open(output_file_path, 'w', encoding='utf-8') as f:
        for label, idx in label_ids.items():
            f.write(u'item {\n')
            f.write(u'\tid: {}\n'.format(idx))
            f.write(u"\tname: '{}'\n".format(label))
            f.write(u'}\n\n')


def dump_detector_annotations(
        db_detector,
        db_user,
        db_dumper,
        scheme,
        host):
    """Dump annotation data for detector training.

    Output is placed into the detector's ondisk dir.
    """
    output_dir = db_detector.get_training_data_dir()
    output_dir.mkdir(parents=True)
    output_labelmap_file_path = output_dir / 'label_map.pbtxt'

    db_trainset = db_detector.trainset
    labels = []
    # call cvat dump tool on each video in the trainset
    for db_video in db_trainset.videos.all():
        db_task = db_video.task
        task_annotations_file_path = dump_cvat_task_annotations(db_task, db_user, db_dumper, scheme, host)
        # cvat's tfrecord does not contain image data. here we add the image
        # data into the tfrecord file as a feature 'image/data'
        add_image_to_cvat_tfrecord(db_task.get_data_dirname(),
                                   task_annotations_file_path,
                                   output_dir / (
                                       os.path.splitext(
                                           os.path.basename(task_annotations_file_path))[0] + '.tfrecord')
                                   )
        task_labels = get_label_map_from_cvat_tfrecord_zip(
            task_annotations_file_path
        )
        labels.extend(task_labels)
        os.remove(task_annotations_file_path)

    _dump_labelmap_file(labels,
                        output_labelmap_file_path)
    split_train_eval_tfrecord(output_dir)


def split_train_eval_tfrecord(data_dir):
    """Split tfrecord in the data_dir into train and eval sets."""
    tfrecord_files = data_dir.glob('*.tfrecord')
    tfrecord_files = [str(tfrecord_file) for tfrecord_file in tfrecord_files]
    dataset = tf.data.TFRecordDataset(tfrecord_files)
    output_train_tfrecord_file_path = str(data_dir / 'train.tfrecord')
    output_eval_tfrecord_file_path = str(data_dir / 'eval.tfrecord')

    # get train/eval item ids
    total_num = 0
    eval_percentage = 0.1
    meta_data = {
        'train_num': 0,
        'eval_num': 0
    }
    for item in iter(dataset):
        total_num += 1
    eval_ids = np.random.choice(total_num,
                                int(eval_percentage * total_num), replace=False)

    with tf.io.TFRecordWriter(output_train_tfrecord_file_path) as train_writer:
        with tf.io.TFRecordWriter(output_eval_tfrecord_file_path) as eval_writer:
            for idx, item in enumerate(iter(dataset)):
                if idx in eval_ids:
                    eval_writer.write(item.numpy())
                    meta_data['eval_num'] += 1
                else:
                    train_writer.write(item.numpy())
                    meta_data['train_num'] += 1
    dump_metadata(
        meta_data,
        data_dir / 'meta'
    )

# def prepare_coco_dataset(annotation_file_path, cvat_image_dir, output_dir):
#     """Create a on-disk coco dataset with both images and annotations.
#     """
#     from pycocotools import coco as coco_loader

#     annotation_file_path = pathlib.Path(annotation_file_path).resolve()
#     output_dir = pathlib.Path(output_dir).resolve()
#     output_dir.mkdir(parents=True, exist_ok=True)

#     # annotation file
#     annotation_file_name = 'annotation.json'
#     os.symlink(annotation_file_path, output_dir / annotation_file_name)

#     # image files
#     output_data_dir = output_dir / 'images'
#     shutil.rmtree(output_data_dir, ignore_errors=True)
#     output_data_dir.mkdir()
#     coco_dataset = coco_loader.COCO(str(annotation_file_path))
#     coco_images = coco_dataset.loadImgs(coco_dataset.getImgIds())
#     cvat_frame_id_regex = re.compile(r'\d+')
#     for coco_image in coco_images:
#         coco_file_name = coco_image['file_name']
#         # cvat uses "frame_{:06d}".format(frame) as default file name
#         # see cvat.annotations.annotation
#         cvat_frame_id = int(cvat_frame_id_regex.findall(coco_file_name)[0])
#         input_image_file_path = _cvat_get_frame_path(cvat_image_dir,
#                                                      cvat_frame_id)
#         output_image_file_path = output_data_dir / coco_file_name
#         os.symlink(input_image_file_path, output_image_file_path)
