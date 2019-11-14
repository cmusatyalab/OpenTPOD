# Copyright (C) 2019 Intel Corporation
#
# SPDX-License-Identifier: MIT

import os
import shutil

from rest_framework import serializers
from opentpod.object_detector import models


class TrainSetSerializer(serializers.ModelSerializer):
    videos = serializers.PrimaryKeyRelatedField(many=True,
                queryset=models.Video.objects.all())
    class Meta:
        model = models.TrainSet
        fields = '__all__'
        read_only_fields = ('created_date', )


class DetectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Detector
        fields = ('url', 'id', 'name', 'owner',
                  'created_date', 'updated_date', 'status')
        read_only_fields = ('created_date', 'updated_date', 'status')
        ordering = ['-id']

    # pylint: disable=no-self-use
    def create(self, validated_data):
        db_task = models.Detector.objects.create(**validated_data)
        # TODO(junjuew): launch bg training job here
        return db_task
