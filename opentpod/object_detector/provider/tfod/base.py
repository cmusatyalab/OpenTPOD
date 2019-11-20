"""Tensorflow Object Detection API provider.
"""
import subprocess
import re
import tempfile
import shutil
import pathlib

from logzero import logger
from mako import template

from opentpod.object_detector.provider import utils


class TFODDetector():
    """Tensorflow Object Detection API
    See: https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/running_locally.md
    """
    REQUIRED_PARAMETERS = []
    OPTIONAL_PARAMETERS = {}

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
        self._input_dir = self._config['input_dir']
        self._output_dir = self._config['output_dir']

        # find appropriate model to finetune from
        self.cache_pretrained_model()

        # fill in on-disk file structure to config
        self._config['pipeline_config_path'] = str(self._input_dir.resolve() / 'pipeline.config')
        self._config['train_input_path'] = str(self._input_dir.resolve() / 'train.tfrecord')
        self._config['eval_input_path'] = str(self._input_dir.resolve() / 'eval.tfrecord')
        self._config['label_map_path'] = str(self._input_dir.resolve() / 'label_map.pbtxt')

    @property
    def required_parameters(self):
        return self.REQUIRED_PARAMETERS

    @property
    def optional_parameters(self):
        return self.OPTIONAL_PARAMETERS

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
        if utils.get_cache_entry(self.pretrained_model_cache_entry) is None:
            logger.info('downloading and caching pretrained model from tensorflow website')
            logger.info('url: {}'.format(self.pretrained_model_url))
            utils.download_and_extract_url_tarball_to_cache_dir(
                self.pretrained_model_url, self.pretrained_model_cache_entry)

    def get_pretrained_model_checkpoint(self):
        cache_entry_dir = utils.get_cache_entry(self.pretrained_model_cache_entry)
        potential_pretained_model_files = list(cache_entry_dir.glob('**/model.ckpt*'))
        if len(potential_pretained_model_files) == 0:
            raise ValueError('Failed to find pretrained model in {}'.format(cache_entry_dir))
        fine_tune_model_dir = potential_pretained_model_files[0].parent
        return str(fine_tune_model_dir.resolve() / 'model.ckpt')

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

        # make sure all required parameter is given
        for parameter in self.required_parameters:
            if parameter not in self._config:
                raise ValueError('Parameter ({}) is required, but not given'.format(parameter))

        # use default values for optional parameters if not given
        for parameter, value in self.optional_parameters.items():
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

    def train(self):
        # need to run tf train with subprocess as tf has problem with python's
        # multiprocess module
        # see: https://github.com/tensorflow/tensorflow/issues/5448
        cmd = 'python -m opentpod.object_detector.provider.tfod.wrappers.train --pipeline_config_path={0} --model_dir={1} --alsologtostderr'.format(
            self._config['pipeline_config_path'],
            self._output_dir
        )
        logger.info('launching training process with following command: \n\n{}'.format(cmd))
        process = subprocess.Popen(
            cmd.split())
        return process.pid

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
        return max_step_model_path

    def export(self, output_file_path):
        with tempfile.TemporaryDirectory() as temp_dir:
            cmd = ('python -m opentpod.object_detector.provider.tfod.wrappers.export ' +
                   '--input_type=image_tensor --pipeline_config_path={} ' +
                   '--trained_checkpoint_prefix={} ' +
                   '--output_directory={} ' +
                   '--alsologtostderr').format(
                self._config['pipeline_config_path'],
                self._get_latest_model_ckpt_path(),
                temp_dir
            )
            logger.info('launching training process with following command: \n\n{}'.format(cmd))
            process = subprocess.Popen(
                cmd.split())
            process.wait()
            file_stem = str(pathlib.Path(output_file_path).parent
                            / pathlib.Path(output_file_path).stem)
            logger.debug(file_stem)
            shutil.make_archive(
                file_stem,
                'zip',
                temp_dir)
            # str(pathlib.Path(temp_dir).parent.resolve()),
            # pathlib.Path(temp_dir).name)
        return process.pid
