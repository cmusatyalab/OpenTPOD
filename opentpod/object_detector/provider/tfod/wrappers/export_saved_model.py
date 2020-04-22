# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# modified by Junjue Wang <junjuew.cs.cmu.edu>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Functions to export object detection inference graph as a SavedModel for TF serving.

Modified from https://github.com/tensorflow/models/blob/master/research/object_detection/exporter.py
based on https://github.com/tensorflow/models/issues/1988.

"""
import os
import tempfile
import tensorflow as tf
from tensorflow.core.protobuf import saver_pb2
from object_detection.core import standard_fields as fields
from object_detection.builders import graph_rewriter_builder
from object_detection.builders import model_builder
from object_detection.utils import config_util
from object_detection.exporter import (build_detection_graph,
                                       profile_inference_graph,
                                       replace_variable_values_with_moving_averages,
                                       write_graph_and_checkpoint)


def write_saved_model(saved_model_path,
                      trained_checkpoint_prefix,
                      inputs,
                      outputs):
    """Writes SavedModel to disk.

    If checkpoint_path is not None bakes the weights into the graph thereby
    eliminating the need of checkpoint files during inference. If the model
    was trained with moving averages, setting use_moving_averages to true
    restores the moving averages, otherwise the original set of variables
    is restored.

    Args:
      saved_model_path: Path to write SavedModel.
      trained_checkpoint_prefix: Prefix of trained checckpoint
      inputs: The input placeholder tensor.
      outputs: A tensor dictionary containing the outputs of a DetectionModel.
    """
    saver = tf.train.Saver()
    with tf.Session() as sess:
        saver.restore(sess, trained_checkpoint_prefix)

        builder = tf.saved_model.builder.SavedModelBuilder(saved_model_path)

        tensor_info_inputs = {
            'inputs': tf.saved_model.utils.build_tensor_info(inputs)}
        tensor_info_outputs = {}
        for k, v in outputs.items():
            tensor_info_outputs[k] = tf.saved_model.utils.build_tensor_info(v)

        detection_signature = (
            tf.saved_model.signature_def_utils.build_signature_def(
                inputs=tensor_info_inputs,
                outputs=tensor_info_outputs,
                method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME
            ))

        builder.add_meta_graph_and_variables(
            sess,
            [tf.saved_model.tag_constants.SERVING],
            signature_def_map={
                tf.saved_model.signature_constants
                .DEFAULT_SERVING_SIGNATURE_DEF_KEY:
                    detection_signature,
            },
        )
        builder.save()


def _export_inference_graph(input_type,
                            detection_model,
                            use_moving_averages,
                            trained_checkpoint_prefix,
                            output_directory,
                            additional_output_tensor_names=None,
                            input_shape=None,
                            output_collection_name='inference_op',
                            graph_hook_fn=None,
                            write_inference_graph=False,
                            temp_checkpoint_prefix=''):
    """Export helper."""
    tf.gfile.MakeDirs(output_directory)
    saved_model_path = os.path.join(output_directory, 'saved_model', '00001')
    model_path = os.path.join(output_directory, 'model.ckpt')

    outputs, placeholder_tensor = build_detection_graph(
        input_type=input_type,
        detection_model=detection_model,
        input_shape=input_shape,
        output_collection_name=output_collection_name,
        graph_hook_fn=graph_hook_fn)

    # OpenTPOD: popping unnecessary outputs for object detection inference.
    # see
    # https://github.com/tensorflow/models/blob/master/research/object_detection/core/standard_fields.py
    outputs.pop(fields.DetectionResultFields.detection_multiclass_scores, None)
    outputs.pop(fields.DetectionResultFields.detection_features, None)
    outputs.pop(fields.DetectionResultFields.detection_masks, None)
    outputs.pop(fields.DetectionResultFields.detection_boundaries, None)
    outputs.pop(fields.DetectionResultFields.detection_keypoints, None)
    outputs.pop(fields.DetectionResultFields.raw_detection_boxes, None)
    outputs.pop(fields.DetectionResultFields.raw_detection_scores, None)
    outputs.pop(fields.DetectionResultFields.detection_anchor_indices, None)

    profile_inference_graph(tf.get_default_graph())
    saver_kwargs = {}
    if use_moving_averages:
        if not temp_checkpoint_prefix:
            # This check is to be compatible with both version of SaverDef.
            if os.path.isfile(trained_checkpoint_prefix):
                saver_kwargs['write_version'] = saver_pb2.SaverDef.V1
                temp_checkpoint_prefix = tempfile.NamedTemporaryFile().name
            else:
                temp_checkpoint_prefix = tempfile.mkdtemp()
        replace_variable_values_with_moving_averages(
            tf.get_default_graph(), trained_checkpoint_prefix,
            temp_checkpoint_prefix)
        checkpoint_to_use = temp_checkpoint_prefix
    else:
        checkpoint_to_use = trained_checkpoint_prefix

    saver = tf.train.Saver(**saver_kwargs)
    input_saver_def = saver.as_saver_def()

    write_graph_and_checkpoint(
        inference_graph_def=tf.get_default_graph().as_graph_def(),
        model_path=model_path,
        input_saver_def=input_saver_def,
        trained_checkpoint_prefix=checkpoint_to_use)
    if write_inference_graph:
        inference_graph_def = tf.get_default_graph().as_graph_def()
        inference_graph_path = os.path.join(output_directory,
                                            'inference_graph.pbtxt')
        for node in inference_graph_def.node:
            node.device = ''
        with tf.gfile.GFile(inference_graph_path, 'wb') as f:
            f.write(str(inference_graph_def))

    if additional_output_tensor_names is not None:
        output_node_names = ','.join(outputs.keys()+additional_output_tensor_names)
    else:
        output_node_names = ','.join(outputs.keys())

    write_saved_model(saved_model_path, trained_checkpoint_prefix,
                      placeholder_tensor, outputs)


def export_inference_graph(input_type,
                           pipeline_config,
                           trained_checkpoint_prefix,
                           output_directory,
                           input_shape=None,
                           output_collection_name='inference_op',
                           additional_output_tensor_names=None,
                           write_inference_graph=False):
    """Exports inference graph for the model specified in the pipeline config.

    Args:
      input_type: Type of input for the graph. Can be one of ['image_tensor',
        'encoded_image_string_tensor', 'tf_example'].
      pipeline_config: pipeline_pb2.TrainAndEvalPipelineConfig proto.
      trained_checkpoint_prefix: Path to the trained checkpoint file.
      output_directory: Path to write outputs.
      input_shape: Sets a fixed shape for an `image_tensor` input. If not
        specified, will default to [None, None, None, 3].
      output_collection_name: Name of collection to add output tensors to.
        If None, does not add output tensors to a collection.
      additional_output_tensor_names: list of additional output
        tensors to include in the frozen graph.
      write_inference_graph: If true, writes inference graph to disk.
    """
    detection_model = model_builder.build(pipeline_config.model,
                                          is_training=False)
    graph_rewriter_fn = None
    if pipeline_config.HasField('graph_rewriter'):
        graph_rewriter_config = pipeline_config.graph_rewriter
        graph_rewriter_fn = graph_rewriter_builder.build(graph_rewriter_config,
                                                         is_training=False)
    _export_inference_graph(
        input_type,
        detection_model,
        pipeline_config.eval_config.use_moving_averages,
        trained_checkpoint_prefix,
        output_directory,
        additional_output_tensor_names,
        input_shape,
        output_collection_name,
        graph_hook_fn=graph_rewriter_fn,
        write_inference_graph=write_inference_graph)
    pipeline_config.eval_config.use_moving_averages = False
    config_util.save_pipeline_config(pipeline_config, output_directory)
