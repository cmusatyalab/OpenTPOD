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
        fields = '__all__'
        read_only_fields = ('created_date', 'updated_date', 'status')

    # def create(self, validated_data):
    #     """Override create to create the nested trainconfig db entry.
    #     This is called before the perform_create in views.py
    #     """
    #     trainconfig_data = validated_data.pop('trainconfig')
    #     db_detector = models.Detector.objects.create(**validated_data)
    #     models.TrainConfig.objects.create(detector=db_detector, **trainconfig_data)
    #     return db_detector
