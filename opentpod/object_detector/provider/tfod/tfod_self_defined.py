from .base import TFODDetector
from django.conf import settings

from logzero import logger
import os

SELFMODELPATH = os.path.join(settings.TRAINMODEL_ROOT, 'modelpath')

class DetectorSelfModel(TFODDetector):
    TRAINING_PARAMETERS = {'batch_size': 2, 'num_steps': 20000}

    def __init__(self, config):
        super().__init__(config)
        logger.info('init self detector')

    @property
    def pretrained_model_url(self):
        logger.info('url ing')
        self.SELFMODEL = ""
        if os.path.exists(SELFMODELPATH):
            premodel = open(SELFMODELPATH, 'r')
            self.SELFMODEL = premodel.read()
            premodel.close()
        return self.SELFMODEL

    @property
    def pipeline_config_template(self):
        logger.info('config ing')
        self.TEMPLATE = ""
        CONFIGPATH = os.path.join(self.SELFMODEL, 'pipeline.config')
        if os.path.exists(CONFIGPATH):
            f = open(CONFIGPATH, 'r')
            self.TEMPLATE = f.read()
            logger.info('update TEMPLATE')
            f.close()
        return self.TEMPLATE
        