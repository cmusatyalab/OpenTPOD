from django.contrib import admin

from django.contrib import admin
from .models import Detector, TrainSet, DetectorModel, ModelPath


admin.site.register(Detector, admin.ModelAdmin)
admin.site.register(TrainSet, admin.ModelAdmin)
admin.site.register(DetectorModel, admin.ModelAdmin)
admin.site.register(ModelPath, admin.ModelAdmin)