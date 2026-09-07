from rest_framework import serializers
from .models import CycleLog

class CycleLogSerializer(serializers.ModelSerializer):
    class Meta: 
        model = CycleLog
        fields = ["id", "user", "start_date","period_duration",]
