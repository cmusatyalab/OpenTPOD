# OpenTPOD

Open-Source Toolkit for Painless Object Detection.

## Motivation

Training a DNN for custom object detection is not trivial. In particular, it
involves constructing a correctly-labeled training data set with millions of
positive and negative examples. The training process itself may take days to
complete, and requires a set of arcane procedures to ensure both convergence and
efficacy of the model. Fortunately, one does not typically need to train a DNN
from scratch. Rather, pretrained models based on public image data sets such as
ImageNet are publicly available. Developers can adapt these pretrained models to
detect custom classes for new applications, through a process called transfer
learning. The key assumption of transfer learning is that much of the training
that teaches the model to discover low-level features, such as edges, textures,
shapes, and patterns that are useful in distinguishing objects can be reused.
Thus, adapting a pretrained model for new object classes requires only thousands
or tens of thousands of examples and hours of training time. However, even with
transfer learning, collecting a labeled training set of several thousand
examples per object class can be a daunting and painful task. In addition,
implementing object detection DNNs itself requires expertise and takes time.

OpenTPOD is a web-based tool to streamline the process of creating DNN-based
object detectors for fast prototyping. It provides an assistive labeling
interface for speedy annotation and a DNN training and evaluation portal that
leverages transfer learning to hide the nuances of DNN creation. It greatly
reduces the labeling effort while constructing a dataset, and automates training
an object detection DNN model.

## Usage Video

https://www.youtube.com/watch?v=B_PX5SSSLJM

## Installation and Deployment

See [docs/server-guide.md](docs/server-guide.md).
