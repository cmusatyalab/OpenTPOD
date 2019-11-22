# Copyright (C) 2019 Intel Corporation
#
# SPDX-License-Identifier: MIT

import os
import shutil

from rest_framework import serializers
from opentpod.object_detector import models
from cvat.apps.engine.serializers import WriteOnceMixin
from cvat.apps.engine.serializers import LabelSerializer, SegmentSerializer
from cvat.apps.engine import models as cvat_models


class SimpleTaskSerializer(serializers.ModelSerializer):
    """A simplied task serializer for showing task information.
    """
    labels = LabelSerializer(many=True, source='label_set', partial=True, read_only=True)
    image_quality = serializers.IntegerField(min_value=0, max_value=100, read_only=True)

    class Meta:
        model = cvat_models.Task
        fields = ('id', 'name', 'size', 'mode', 'owner', 'assignee',
                  'bug_tracker', 'created_date', 'updated_date', 'overlap',
                  'status', 'labels', 'image_quality', 'start_frame',
                  'stop_frame', 'frame_filter')
        read_only_fields = ('name', 'size', 'mode', 'owner', 'assignee',
                            'bug_tracker', 'created_date', 'updated_date', 'overlap',
                            'status', 'labels', 'image_quality', 'start_frame',
                            'stop_frame', 'frame_filter')
        ordering = ['-id']


class TrainSetSerializer(serializers.ModelSerializer):
    # same as DetectorSerializer trick
    # here a trainset object can be created with a list of task ids via POST
    # while GET returns the whole Task object
    tasks = SimpleTaskSerializer(many=True, read_only=True)
    tasks_id = serializers.PrimaryKeyRelatedField(
        source='tasks',
        many=True,
        queryset=models.Task.objects.all(),
        write_only=True)

    class Meta:
        model = models.TrainSet
        fields = '__all__'
        read_only_fields = ('created_date', )


class DetectorSerializer(WriteOnceMixin, serializers.ModelSerializer):
    # a workaround to return full object when read
    # but only needs object id for write.
    # Otherwise, such behavior needs to be manually implemented in create()
    # By default, drf doens't automatically implement nested writable fields.
    # see: https://github.com/encode/django-rest-framework/issues/5206
    train_set = TrainSetSerializer(read_only=True)
    # the 'id' field of 'train_set'
    train_set_id = serializers.PrimaryKeyRelatedField(
        source='train_set',
        queryset=models.TrainSet.objects.all(),
        write_only=True
    )

    class Meta:
        model = models.Detector
        fields = '__all__'
        read_only_fields = ('created_date', 'updated_date')
        write_once_fields = ('dnn_type', 'parent', 'train_set', 'train_config')
