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
    # a workaround to return full object when read
    # but only needs object id for write.
    # Otherwise, such behavior needs to be manually implemented in create()
    # By default, drf doens't automatically implement nested writable fields.
    # see: https://github.com/encode/django-rest-framework/issues/5206
    # here a trainset object can be created with a list of task ids via POST
    # while GET returns the whole Task object
    tasks = SimpleTaskSerializer(many=True, read_only=True)
    # the 'id' field of 'tasks'
    tasks_id = serializers.PrimaryKeyRelatedField(
        source='tasks',
        many=True,
        queryset=models.Task.objects.all(),
        write_only=True)

    class Meta:
        model = models.TrainSet
        fields = '__all__'
        read_only_fields = ('created_date', )


class ModelPathSerializer(serializers.ModelSerializer):
    tasks = SimpleTaskSerializer(many=True, read_only=True)
    class Meta:
        model = models.ModelPath
        fields = '__all__'
        read_only_fields = ('created_date', )

class DetectorModelSerializer(serializers.ModelSerializer):
    tasks = SimpleTaskSerializer(many=True, read_only=True)
    class Meta:
        model = models.DetectorModel
        fields = '__all__'
        read_only_fields = ('created_date', )

class DetectorSerializer(WriteOnceMixin, serializers.ModelSerializer):
    train_set = TrainSetSerializer()

    class Meta:
        model = models.Detector
        fields = '__all__'
        read_only_fields = ('created_date', 'updated_date', 'status')
        write_once_fields = ('dnn_type', 'parent', 'train_set', 'train_config')

    def _fix_owner(self, data):
        owner = self.context['request'].user
        if data.get('owner', None) is None:
            data['owner'] = owner

    def create(self, validated_data):
        # ignore the owner fields, as we'll only create it for the user
        self._fix_owner(validated_data)

        # create train_set db object
        train_set_data = validated_data.pop('train_set')
        self._fix_owner(train_set_data)
        tasks = train_set_data.pop('tasks')
        db_train_set = models.TrainSet.objects.create(
            **train_set_data)
        db_train_set.tasks.set(tasks)
        db_train_set.save()

        # status can only be created
        validated_data['status'] = str(models.Status.CREATED)
        db_detector = models.Detector.objects.create(**validated_data,
                                                     train_set=db_train_set)
        return db_detector
