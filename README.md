# OpenTPOD

*Create deep learning based object detectors without writing a single line of code.*

OpenTPOD is an all-in-one open-source tool for nonexperts to create custom deep
neural network object detectors. It is designed to lower the barrier of entry
and facilitates the end-to-end authoring workflow of custom object detection
using state-of-art deep learning methods.

It provides the following features via an easy-to-use web interface.

* Training data management.
* Data annotation through seamless integration with [OpenCV CVAT Labeling Tool](https://github.com/opencv/cvat).
* One-click training/fine-tuning of object detection deep neural networks,
  including SSD MobileNet, Faster RCNN Inception, and Faster RCNN ResNet.
* One-click model export for inference with Tensorflow Serving.
* Extensible architecture for easy addition of new deep neural network architectures.

## Demo Video

[![OpenTPOD Demo Video](http://img.youtube.com/vi/UHnNLrD6jTo/0.jpg)](https://youtu.be/UHnNLrD6jTo)


## Documentation

* [Motivation](docs/motivation.md)
* [User Guide](docs/user-guide.md)
* [Installation and Administration Guide](docs/server-guide.md)
* [Developer Guide](docs/notes.md)

## Citations

Please cite the following thesis if you find OpenTPOD helps your research.

```
@phdthesis{wang2020scaling,
  title={Scaling Wearable Cognitive Assistance},
  author={Wang, Junjue},
  year={2020},
  school={CMU-CS-20-107, CMU School of Computer Science}
}
```

## Acknowledgement

This research was supported by the National Science Foundation (NSF) under grant
number CNS-1518865. Additional support was provided by Intel, Vodafone, Deutsche
Telekom, Verizon, Crown Castle, Seagate, VMware, MobiledgeX, InterDigital, and
the Conklin Kistler family fund.
