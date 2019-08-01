# Copyright (C) 2019 Intel Corporation
#
# SPDX-License-Identifier: MIT

import os
import shutil

from rest_framework import serializers
from opentpod.object_detector import models


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