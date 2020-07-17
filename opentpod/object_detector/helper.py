from logzero import logger
from django.conf import settings
import shutil
import zipfile
import threading
import os.path
import time

import pathlib
import json
import enum
import os
import re

SELFMODELPATH = os.path.join(settings.TRAINMODEL_ROOT, 'modelpath')

def unzippedFile(path, id, name):
    # logger.info("get to unzip func")
    logger.info(path)
    while not os.path.exists(path):
        time.sleep(3)
        
    # logger.info("file gets existed")
    
    newpath = name
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(path=newpath)
        logger.info("extracting: " + str(newpath))

    # if os.path.exists(os.path.join(newpath, 'meta')):
    #     os.remove(os.path.join(newpath, 'meta'))
    
    # if from detector folder, the remove not needed
    # os.remove(path)
    # logger.info("gets extracted")
    return newpath

def updateConfig(path):
    logger.info(path)
    cg = open(path, 'r')
    contents = cg.readlines()
    # logger.info(contents)
    trainFlag = True
    result = ""
    for i in contents:
        if 'num_classes:' in i:
            result += '    num_classes: ${num_classes}\n'
        elif 'batch_size:' in i:
            result += ' batch_size: ${batch_size}\n'
        elif 'fine_tune_checkpoint:' in i:
            result += '  fine_tune_checkpoint: "${fine_tune_checkpoint}"\n'
        elif 'num_steps:' in i:
            result += ' num_steps: ${num_steps}\n'
        elif 'label_map_path:' in i:
            result += ' label_map_path: "${label_map_path}"\n'
        elif 'input_path:' in i:
            if trainFlag:
                result += '    input_path: "${train_input_path}"\n'
                trainFlag = False
            else:
                result += '    input_path: "${eval_input_path}"\n'
        else:
            result += i
    
    # logger.info(result)
    cg.close()
    cg = open(path, 'w')
    cg.write(result)
    cg.close()

    return result

def set2model(path):
    writefile = open(SELFMODELPATH, 'w+')
    writefile.write(str(path))
    writefile.close()

class Zip2Model():
    def __init__(self, path, id):
        logger.info(path)
        logger.info(id)
        name = str(path)[:-4]
        # if not str(path).endswith('.zip'):
        #     raise FileError("only zip can accepted")
        logger.info(name)
        self.file = unzippedFile(path, id, name)
        self.configPath = os.path.join(self.file, 'pipeline.config')
        # logger.info(self.configPath)
        self.newconfig = updateConfig(self.configPath)
        # os.remove(self.configPath)
        # with open(self.configPath, 'w') as cg:
        # set2model(self.file)


