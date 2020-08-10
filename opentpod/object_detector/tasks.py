"""Background tasks for object_detector
"""
import sys
import traceback

import django_rq
from logzero import logger

from . import datasets, models


def _train(db_detector,
           db_tasks,
           db_user,
           scheme,
           host):
    """Launch the transfer learning of a DNN."""
    # dump annotations
    if db_detector.dnn_type == 'GoogleAutoML':
        datasets.dump_detector_annotations4google_cloud(db_detector,
                                       db_tasks,
                                       db_user,
                                       scheme,
                                       host)
    elif db_detector.dnn_type == 'pytorch_classfication_resnet18':
        datasets.dump_detector_annotations4classfication(db_detector,
                                       db_tasks,
                                       db_user,
                                       scheme,
                                       host)
    else:
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
    # logger.info(db_detector.name)
    # logger.info(db_detector.dnn_type)

    try:
        if db_detector.dnn_type == 'GoogleAutoML':
            project_id, dataset_id = detector.importData(db_detector)
            detector.cloudTrain(db_detector, project_id, dataset_id)
        elif db_detector.dnn_type == 'pytorch_classfication_resnet18':
            logger.info('get to pytorch classfication')
            detector.pytorchtrain(db_detector)
        else:
            detector.prepare(db_detector.getId())
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
    """Export DNN"""
    detector = db_detector.get_detector_object()
    # if db_detector.dnn_type == 'GoogleAutoML':
    #     detector.export4google(db_detector.get_export_file_path(), db_detector.get_dir())
    # # elif db_detector.dnn_type == 'Pytorch-Classfication':
    # #     detector.export4pytorch_classfication(db_detector.get_export_file_path(), db_detector.get_dir())
    # else:
    detector.export(db_detector.get_export_file_path(), db_detector.get_dir())


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
