"""Example script to show how to send requests to TF serving to get prediction results

TF server can be started with the following command. The $(pwd) should be where the exported
model is unzipped.

docker run -it --name=test --rm -p 8500:8500 -v $(pwd):/models/myObjectDetector \
-e MODEL_NAME=myObjectDetector tensorflow/serving:latest-gpu
"""
import cv2
import fire
import numpy as np
import tensorflow as tf
from grpc.beta import implementations
from logzero import logger
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2


class TFServingPredictor():
    def __init__(self, host, port, model_name):
        self.channel = implementations.insecure_channel(host, int(port))
        self.stub = prediction_service_pb2.beta_create_PredictionService_stub(self.channel)
        self.model_name = model_name

    def infer_file(self, image_file_path):
        image = cv2.imread(image_file_path)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return self.infer(np.stack([rgb_image.astype(dtype=np.uint8)], axis=0))

    def infer(self, images):
        # Create prediction request object
        request = predict_pb2.PredictRequest()
        # Specify model name (must be the same as when the TensorFlow serving serving was started)
        request.model_spec.name = self.model_name
        # Initalize prediction
        request.inputs['inputs'].CopyFrom(
            tf.make_tensor_proto(images))
        # Call the prediction server
        result = self.stub.Predict(request, 10.0)  # 10 secs timeout
        # convert tensorProto to numpy array
        parsed_results = {}
        for k, v in result.outputs.items():
            parsed_results[k] = tf.make_ndarray(v)
        # fix output result types
        if 'detection_classes' in parsed_results:
            parsed_results['detection_classes'] = parsed_results['detection_classes'].astype(np.int64)
        return parsed_results


def stream_predict(camera_uri, host, port, model_name, label_map_file_path, min_score_thresh=0.8):
    camera = cv2.VideoCapture(camera_uri)
    predictor = TFServingPredictor(host, port, model_name)
    category_index = label_map_util.create_category_index_from_labelmap(
        label_map_file_path, use_display_name=True)

    while True:
        _, image = camera.read()
        if image is not None:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = predictor.infer(
                np.stack([rgb_image.astype(dtype=np.uint8)], axis=0)
            )
            vis_util.visualize_boxes_and_labels_on_image_array(
                rgb_image,
                np.squeeze(results['detection_boxes'], axis=0),
                np.squeeze(results['detection_classes'], axis=0),
                np.squeeze(results['detection_scores'], axis=0),
                category_index,
                instance_masks=None,
                use_normalized_coordinates=True,
                min_score_thresh=min_score_thresh,
                line_thickness=8)
            cv2.imshow('input', cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR))
            cv2.waitKey(1)
        else:
            break
    camera.release()


if __name__ == "__main__":
    fire.Fire(stream_predict)
