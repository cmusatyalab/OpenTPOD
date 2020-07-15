"""Tensorflow Object Detection API provider.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import time

import os
import psutil
from django.http import Http404
from logzero import logger
from mako import template
from proxy.views import proxy_view

from opentpod.object_detector.provider import utils


class TFODDetector():
    """Tensorflow Object Detection API
    See: https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/running_locally.md
    """
    TRAINING_PARAMETERS = {}

    def __init__(self, config):
        """Expected directory layout
            +train-data
                -label_map file
                -train TFRecord file
                -eval TFRecord file
            +models
                + model
                    -pipeline config file
                    +train
                    +eval
        Arguments:
            config: contains input_dir, output_dir, and training parameters
        Output:
            ``${output_dir}/status`` file: training status
            ``${output_dir}/train.log`` file: training log file
        """
        super().__init__()
        self._config = config
        self._input_dir = pathlib.Path(self._config['input_dir'])
        self._output_dir = pathlib.Path(self._config['output_dir'])

        # find appropriate model to finetune from
        self.cache_pretrained_model()

        # fill in on-disk file structure to config
        self._config['pipeline_config_path'] = str(self._input_dir.resolve() / 'pipeline.config')
        self._config['train_input_path'] = str(self._input_dir.resolve() / 'train.tfrecord')
        self._config['eval_input_path'] = str(self._input_dir.resolve() / 'eval.tfrecord')
        self._config['label_map_path'] = str(self._input_dir.resolve() / 'label_map.pbtxt')
        self._config['meta'] = str(self._input_dir.resolve() / 'meta')

    @property
    def training_parameters(self):
        return self.TRAINING_PARAMETERS

    @property
    def pretrained_model_cache_entry(self):
        return self.__class__.__name__ + '-pretrained-model'

    @property
    def pretrained_model_url(self):
        raise NotImplementedError()

    @property
    def pipeline_config_template(self):
        raise NotImplementedError()

    def cache_pretrained_model(self):
        """Download and cache pretrained model if not existed."""
        if str(self.__class__.__name__) != 'DetectorSelfModel':
            if utils.get_cache_entry(self.pretrained_model_cache_entry) is None:
                logger.info('downloading and caching pretrained model from tensorflow website')
                logger.info('url: {}'.format(self.pretrained_model_url))
                utils.download_and_extract_url_tarball_to_cache_dir(
                    self.pretrained_model_url, self.pretrained_model_cache_entry)

    def get_pretrained_model_checkpoint(self):
        logger.info('get to get ckpt')
        if str(self.__class__.__name__) != 'DetectorSelfModel':
            cache_entry_dir = utils.get_cache_entry(self.pretrained_model_cache_entry)
            potential_pretained_model_files = list(cache_entry_dir.glob('**/model.ckpt*'))
            if len(potential_pretained_model_files) == 0:
                raise ValueError('Failed to find pretrained model in {}'.format(cache_entry_dir))
            fine_tune_model_dir = potential_pretained_model_files[0].parent
            return str(fine_tune_model_dir.resolve() / 'model.ckpt')
        else:
            logger.info(str(os.path.join(self.pretrained_model_url, 'model.ckpt')))
            if self.pretrained_model_url == '':
                return None # raise error
            return str(os.path.join(self.pretrained_model_url, 'model.ckpt'))

    def prepare_config(self):
        # num_classes are the number of classes to learn
        with open(self._config['label_map_path'], 'r') as f:
            content = f.read()
            labels = re.findall(r"\tname: '(\w+)'\n", content)
            self._config['num_classes'] = len(labels)

        # fine_tune_checkpoint should point to the path of the checkpoint from
        # which transfer learning is done
        if ('fine_tune_checkpoint' not in self._config) or (
                self._config['fine_tune_checkpoint'] is None):
            self._config['fine_tune_checkpoint'] = self.get_pretrained_model_checkpoint()

        # use default values for training parameters if not given
        for parameter, value in self.training_parameters.items():
            if parameter not in self._config:
                self._config[parameter] = value

    def prepare_config_pipeline_file(self):
        pipeline_config = template.Template(
            self.pipeline_config_template).render(**self._config)
        with open(self._config['pipeline_config_path'], 'w') as f:
            f.write(pipeline_config)

    def prepare(self):
        """Prepare files needed for training."""
        self.prepare_config()
        self.prepare_config_pipeline_file()

    def _check_training_data_dir(self, FLAGS):
        """Check training directory's data is valid

        Fail if missing files, or # of training/eval examples used is not positive
        """
        training_data_dir = pathlib.Path(FLAGS.pipeline_config_path).parent
        assert (training_data_dir / 'meta').resolve().exists()
        assert (training_data_dir / 'label_map.pbtxt').resolve().exists()
        assert (training_data_dir / 'label_map.pbtxt').resolve().stat().st_size > 0
        assert (training_data_dir / 'train.tfrecord').resolve().exists()
        with open(training_data_dir / 'meta', 'r') as f:
            meta = json.load(f)
            assert(meta["train_num"] > 0)
            assert(meta["eval_num"] > 0)

    def train(self):
        """Launch training using tensorflow object detection API."""
        from absl import flags
        from object_detection import model_main as continuous_train_and_eval_model

        # TF uses absl to get command line flags
        FLAGS = flags.FLAGS
        # argv[0] is treated as program name, therefore not parsed
        argv = ['',
                '--pipeline_config_path={}'.format(self._config['pipeline_config_path']),
                '--model_dir={}'.format(self._output_dir),
                '--alsologtostderr']
        logger.info('\n===========================================\n')
        logger.info('\n\nlaunching training with the following parameters: \n{}\n\n'.format(
            '\n'.join(argv)))
        # logger.info('luanzhen: config path: {}\n'.format(self._config['pipeline_config_path']))
        # logger.info('luanzhen: output path: {}\n'.format(self._output_dir))
        # logger.info('luanzhen: this is a test2\n')
        logger.info('\n===========================================\n')
        FLAGS(argv)
        self._check_training_data_dir(FLAGS)
        continuous_train_and_eval_model.main([])

    def run(self):
        pass

    def _get_latest_model_ckpt_path(self):
        candidates = [str(candidate.resolve()) for
                      candidate in self._output_dir.glob('**/model.ckpt*')]
        max_step_model_path = candidates[0]
        max_steps = re.findall(r'model.ckpt-(\d+)', max_step_model_path)[0]
        for candidate_path in candidates:
            trained_steps = re.findall(r'model.ckpt-(\d+)', candidate_path)[0]
            if trained_steps > max_steps:
                max_step_model_path = candidate_path
        # the max_step_model_path now is a full of e.g.
        # .../model-ckpt-2000.data-00000-of-00001
        # however, for TF's export code, we need to give  .../model-ckpt-2000
        # as there are multiple files ending in .meta, .index, .data-...
        return os.path.splitext(max_step_model_path)[0]

    def export(self, output_file_path):
        """Export TF model.
        Both the frozen graph and training artifacts are exported to allow
        inference and future training.

        Note: Since TF's object detection API is not using TF v2.0. We had to
        run the export script in a separate process with TF eager mode disabled.
        CVAT and object_detector.datasets enable TF eager mode for easy
        read/write TFrecord files, causing the following model export script to
        throw errors due to calls to tf.placeholder(). See more at:
        https://github.com/tensorflow/tensorflow/issues/18165

        When TF object detection has migrated to TF v2.0, something like train()
        can be done to directly call the export script as a python function.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cmd = ('python -m opentpod.object_detector.provider.tfod.wrappers.export_inference_graph ' +
                   '--input_type=image_tensor --pipeline_config_path={} ' +
                   '--trained_checkpoint_prefix={} ' +
                   '--output_directory={} ' +
                   '--alsologtostderr').format(
                self._config['pipeline_config_path'],
                self._get_latest_model_ckpt_path(),
                temp_dir
            )
            logger.info('\n===========================================\n')
            logger.info('\n\nExporting trained model with following command: \n\n{}'.format(cmd))
            # logger.info('test4: path: {} {}\n'.format(str(temp_dir), type(temp_dir)))
            # logger.info('test4: output_file_path: {}\n'.format(output_file_path))
            logger.info('\n===========================================\n')
            process = subprocess.Popen(
                cmd.split())
            process.wait()

            # copy some useful training files to export as well
            # shutil.copy2(self._config['pipeline_config_path'], temp_dir)
            subdir = temp_dir + '/data'
            # subdir_model = temp_dir + '/model'
            os.makedirs(subdir)
            # os.makedirs(subdir_model)
            # filesrc = temp_dir + 'model.ckpt.*'
            shutil.copy2(self._config['label_map_path'], temp_dir)
            shutil.copy2(self._config['meta'], temp_dir)
            shutil.copy2(self._config['train_input_path'], subdir)
            shutil.copy2(self._config['eval_input_path'], subdir)
            # shutil.move(filesrc, subdir_model)

            file_stem = str(pathlib.Path(output_file_path).parent
                            / pathlib.Path(output_file_path).stem)
            logger.debug(file_stem)
            shutil.make_archive(
                file_stem,
                'zip',
                temp_dir)

    def _is_tensorboard_subprocess_running(self, pinfo_file_path):
        if pinfo_file_path.exists():
            with open(pinfo_file_path, 'r') as f:
                subprocess_info = json.loads(f.read())
                pid = subprocess_info['pid']
                port = subprocess_info['port']
                try:
                    p = psutil.Process(pid)
                    for connection in p.connections():
                        if connection.laddr[1] == port:
                            # if the process is still running
                            # no need to launch a new process
                            if connection.status == psutil.CONN_LISTEN:
                                return True
                            else:
                                # the process is somehow no longer listening on
                                # the correct port try kill it
                                p.kill()
                except psutil.NoSuchProcess as e:
                    logger.info('No tensorboard process serving directory: {}'.format(
                        self._output_dir))
        return False

    def _run_tensorboard_subprocess(self, pinfo_file_path):
        port = utils._find_open_port()
        cmd = ('tensorboard ' +
               '--logdir={} '.format(self._output_dir) +
               '--host=localhost ' +
               '--port={}'.format(port))
        logger.info('\n===========================================\n')
        logger.info('\n\tStarting Tensorboard with following command: \n\n{}'.format(cmd))
        logger.info('\n===========================================\n')
        process = subprocess.Popen(
            cmd.split())
        with open(pinfo_file_path, 'w') as f:
            f.write(json.dumps({'pid': process.pid, 'port': port}))
        time.sleep(5)

    def _run_tensorboard_subprocess_if_not_exist(self, pinfo_file_path):
        is_running = self._is_tensorboard_subprocess_running(pinfo_file_path)
        if not is_running:
            self._run_tensorboard_subprocess(pinfo_file_path)

    def visualize(self, request, path):
        """Render visualization for current model.

        (A hacky implementation) This method tries to launch a tensorboard
        subprocess and then proxy django requests to it for visualization.
        The subprocess information is stored in a file in the model directory to
        record whether a process has been launched and the port it listens to.
        This implementation can leads to many process (max is the # of detectors
        available) being launched.

        Arguments:
            request {django http request} -- request coming in
            path {request path} -- http request path stripped of api prefixes

        Raises:
            Http404: [description]
            Http404: [description]

        Returns:
            Django HTTP response -- Returns a Django HTTP response for visualization.
        """
        if not self._output_dir.exists():
            raise Http404('Model directory not exists. Has the model been trained?')

        # tensorboard needs index.html to load correctly
        if len(path) == 0:
            path = 'index.html'

        pinfo_file_path = (self._output_dir / 'tensorboard.pinfo').resolve()
        self._run_tensorboard_subprocess_if_not_exist(pinfo_file_path)
        if pinfo_file_path.exists():
            with open(pinfo_file_path, 'r') as f:
                subprocess_info = json.loads(f.read())
                port = subprocess_info['port']
            remoteurl = 'http://localhost:{}/'.format(port) + path
            return proxy_view(request, remoteurl)
        else:
            raise Http404
