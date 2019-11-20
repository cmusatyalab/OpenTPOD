from django.contrib import admin

from django.contrib import admin
from .models import Detector, TrainSet


admin.site.register(Detector, admin.ModelAdmin)
admin.site.register(TrainSet, admin.ModelAdmin)
