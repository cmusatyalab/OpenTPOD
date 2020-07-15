# Generated by Django 2.2.10 on 2020-07-02 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('object_detector', '0016_auto_20200629_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detector',
            name='dnn_type',
            field=models.CharField(choices=[('tensorflow_faster_rcnn_resnet101', 'Tensorflow Faster-RCNN ResNet 101'), ('tensorflow_faster_rcnn_resnet50', 'Tensorflow Faster-RCNN ResNet 50'), ('tensorflow_ssd_mobilenet_v2', 'Tensorflow SSD MobileNet V2'), ('Self-trained', 'Self-trained')], max_length=32),
        ),
    ]
