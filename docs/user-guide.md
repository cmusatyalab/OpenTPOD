---
description: 'Usage Demo Video:https://www.youtube.com/watch?v=B_PX5SSSLJM'
---

# User Guide

### Collect Training Videos

Make sure to collect short video snippets from various viewing angles.

### Annotate

### Start Training

### Download

### Inference

```
$ docker run -it --name=test --rm -p 8500:8500 -v (pwd)/saved_model:/models/myObjectDetector -e MODEL_NAME=myObjectDetector tensorflow/serving
$ cd opentpod/object_detector/provider/tfod && python infer.py
```

{% hint style="info" %}
 Super-powers are granted randomly so please submit an issue if you're not happy with yours.
{% endhint %}

Once you're strong enough, save the world:

{% code title="hello.sh" %}
```bash
# Ain't no code for that yet, sorry
echo 'You got to trust me on this, I saved the world'
```
{% endcode %}



