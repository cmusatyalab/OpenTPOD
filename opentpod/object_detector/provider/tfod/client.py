"""Example script to show how to send requests to TF serving to get prediction results

TF server can be started with the following command. The $(pwd) should be where the exported
model is unzipped.

docker run -it --name=test --rm -p 8500:8500 -v $(pwd):/models/myObjectDetector \
-e MODEL_NAME=myObjectDetector tensorflow/serving:latest-gpu
"""
from PIL import Image
from grpc.beta import implementations
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2
import tensorflow as tf
import numpy as np
import click
from logzero import logger

@click.command()
@click.argument('host')
@click.argument('port')
@click.argument('model_name')
@click.argument('image_file_path', type=click.Path(exists=True))
def infer(host, port, model_name, image_file_path):
    channel = implementations.insecure_channel(host, int(port))
    stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

    # Create prediction request object
    request = predict_pb2.PredictRequest()

    # Specify model name (must be the same as when the TensorFlow serving serving was started)
    request.model_spec.name = model_name

    image = np.asarray(Image.open(image_file_path))
    height, width, channel = image.shape

    # Initalize prediction
    request.inputs['inputs'].CopyFrom(
            tf.contrib.util.make_tensor_proto(image.astype(dtype=np.uint8), 
            shape=[1, height, width, channel]))

    # Call the prediction server
    result = stub.Predict(request, 10.0)  # 10 secs timeout
    logger.info(result)

# # Plot boxes on the input image
# category_index = load_label_map(FLAGS.path_to_labels)
# boxes = result.outputs['detection_boxes'].float_val
# classes = result.outputs['detection_classes'].float_val
# scores = result.outputs['detection_scores'].float_val
# image_vis = vis_util.visualize_boxes_and_labels_on_image_array(
#     FLAGS.input_image,
#     np.reshape(boxes,[100,4]),
#     np.squeeze(classes).astype(np.int32),
#     np.squeeze(scores),
#     category_index,
#     use_normalized_coordinates=True,
#     line_thickness=8)

# # Save inference to disk
# scipy.misc.imsave('%s.jpg'%(FLAGS.input_image), image_vis)

if __name__ == "__main__":
    infer()