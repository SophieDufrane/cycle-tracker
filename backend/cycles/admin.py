from django.contrib import admin
from .models import CycleLog, CycleConfig

@admin.register(CycleLog)
class CycleLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "start_date","period_duration",)
    list_filter = ("user","start_date",)

@admin.register(CycleConfig)
class CycleConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "value",)

