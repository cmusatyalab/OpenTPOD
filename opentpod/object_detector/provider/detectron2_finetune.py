# -*- coding: utf-8 -*-
import os
import random
import time

import cv2
import detectron2
import matplotlib.pyplot as plt
import numpy as np
from detectron2.config import get_cfg
from detectron2 import data as dtn_data
from detectron2 import engine as dtn_engine
from detectron2.utils.logger import setup_logger
from detectron2 import utils as dtn_utils
# utils.visualizer import ColorMode, Visualizer

setup_logger()


def load_dataset(name, annotation_file_path, image_dir):
    """Load coco dataset."""
    dtn_data.datasets.register_coco_instances(name,
                                              {},
                                              annotation_file_path, image_dir)
    return dtn_data.MetadataCatalog.get(name), dtn_data.DatasetCatalog.get(name)


def _visualize_training_samples(
        dataset_metadata,
        dataset_catalog):
    """To verify the data loading is correct, let's visualize the annotations of randomly selected samples in the training set:"""
    for sample in random.sample(dataset_catalog, 3):
        img = cv2.imread(sample["file_name"])
        visualizer = dtn_utils.visualizer.Visualizer(img[:, :, ::-1], metadata=dataset_metadata, scale=0.5)
        vis = visualizer.draw_dataset_dict(d)
        cv2.imshow(vis.get_image()[:, :, ::-1])
        cv2.waitKey(0)


def finetune():
    """let's fine-tune a coco-pretrained R50-FPN Mask R-CNN model on the fruits_nuts dataset.
    It takes ~6 minutes to train 300 iterations on Colab's K80 GPU."""
    cfg = get_cfg()
    cfg.merge_from_file("./detectron2_repo/configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
    cfg.DATASETS.TRAIN = ("fruits_nuts",)
    cfg.DATASETS.TEST = ()   # no metrics implemented for this dataset
    cfg.DATALOADER.NUM_WORKERS = 2
    # initialize from model zoo
    cfg.MODEL.WEIGHTS = "detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl"
    cfg.SOLVER.IMS_PER_BATCH = 2
    cfg.SOLVER.BASE_LR = 0.02
    cfg.SOLVER.MAX_ITER = 300    # 300 iterations seems good enough, but you can certainly train longer
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128   # faster, and good enough for this toy dataset
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 3  # 3 classes (data, fig, hazelnut)

    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    trainer = dtn_engine.DefaultTrainer(cfg)
    trainer.resume_or_load(resume=False)
    trainer.train()


def infer(cfg, infer_dicts, dataset_metadata):
    """Now, we perform inference with the trained model on the fruits_nuts dataset. First, let's create a predictor using the model we just trained:"""
    cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5   # set the testing threshold for this model
    cfg.DATASETS.TEST = ("fruits_nuts", )
    predictor = dtn_engine.DefaultPredictor(cfg)

    """Then, we randomly select several samples to visualize the prediction results."""
    for d in random.sample(infer_dicts, 3):
        im = cv2.imread(d["file_name"])
        outputs = predictor(im)
        v = dtn_utils.visualizer.Visualizer(im[:, :, ::-1],
                                            metadata=dataset_metadata,
                                            scale=0.8,
                                            instance_mode=dtn_utils.visualizer.ColorMode.IMAGE_BW   # remove the colors of unsegmented pixels
                                            )
        v = v.draw_instance_predictions(outputs["instances"].to("cpu"))
        cv2.imshow(v.get_image()[:, :, ::-1])


def benchmark_speed(predictor):
    """## Benchmark inference speed"""
    times = []
    for i in range(20):
        start_time = time.time()
        outputs = predictor(im)
        delta = time.time() - start_time
        times.append(delta)
    mean_delta = np.array(times).mean()
    fps = 1 / mean_delta
    print("Average(sec):{:.2f},fps:{:.2f}".format(mean_delta, fps))
