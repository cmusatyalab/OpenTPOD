# Generated by Django 2.2.10 on 2020-07-03 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('object_detector', '0019_auto_20200703_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detectormodel',
            name='name',
            field=models.CharField(max_length=256, unique=True),
        ),
    ]
