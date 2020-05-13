---
description: Explains how to use OpenTPOD to create custom object detectors.
---

# User Guide

Watch the Usage Demo Video: [https://www.youtube.com/watch?v=B\_PX5SSSLJM](https://www.youtube.com/watch?v=B_PX5SSSLJM)

### Collect Training Videos

Using OpenTPOD to create object detectors is straight-forward. A developer first captures videos of objects from various viewing angles and diverse backgrounds. For example, these videos can be acquired on a mobile phone. At 30 frames per second, ten minutes of video footage contain 18000 frames, which is already a reasonable amount of training data for transfer learning. Larger amounts of training data typically help increase the accuracy, although diminishing returns apply. Moreover, it is preferred to collect training examples in environment similar to the test environment to make the training examples exhibit similar distribution as test data. 

Note that the image background is randomly cropped to be used as negative examples. These background examples illustrate to the neural network what an object of interest does not look like. Therefore, it is recommended that the background contains common objects in the test environment that may cause confusion.

### Annotate

OpenTPOD assists users to annotate the training videos by integrating an external labeling tool into the GUI. Uers can annotate objects by draw bounding boxes on the uploaded video frames. To facilitate the annotation process, OpenTPOD leverages the fact that the individual frames come from a continuous video shoot. It automatically generates bounding box in subsequent frames using linear interpolation. As a result, users only need to label a few key frames in a video with the rest of frames auto-populated with generated labels. 

The details on how to use the annotation tool can be found [here](https://github.com/opencv/cvat/blob/v0.4.1/cvat/apps/documentation/user_guide.md#interface-of-the-annotation-tool). **Note: Make sure to save your annotations by clicking "Open Menu >> Save Work".**

### Launch Training

Go to "Detector" tab and fill out the training form to launch the DNN training
process without writing a single line of code. Under the hood, OpenTPOD
automates the transfer learning process. OpenTPOD supports several
state-of-the-art object detection networks, including FasterRCNN-ResNet and
SSD-MobileNet. These different networks exhibit varying accuracy versus speed
trade-offs. While FasterRCNN-ResNet achieves higher accuracies on standard
datasets, its training and inference time are significantly longer than
SSD-MobileNet. Application developers should choose the appropriate DNN network
based on their accuracy and latency constraints. Negative examples are mined
from the video background; these are parts of the frames not included in the
object bounding boxes. The OpenTPOD web GUI provides training monitoring through
Tensorflow visualization library Tensorboard.

### Download

The training process generates downloadable Tensorflow models in the end. Click on the "Download" button to download the model.

### Inference

Extract the downloaded zip file and serve the "saved\_model" directory with Tensorflow serving container image. 

* Go into the directory of "saved\_model". The current directory should have subdirectories names like "00001", etc.
* Run the following command.

It will start a gRPC server at port 8500 and a HTTP/JSON server at port 8501.

```
$ docker run -it --name=inference --rm\
  -p 8500:8500 -p 8501:8501\
  -v $(pwd)/saved_model:/models/myObjectDetector\
  -e MODEL_NAME=myObjectDetector tensorflow/serving
```

An example client code to query TF serving container can be found under [opentpod/object\_detector/provider/tfod/infer.py](https://github.com/junjuew/OpenTPOD/blob/master/opentpod/object_detector/provider/tfod/infer.py).

