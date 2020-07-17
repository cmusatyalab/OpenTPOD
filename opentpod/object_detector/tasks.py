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
        # logger.info(db_user)
        # logger.info(db_detector.getId())
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
