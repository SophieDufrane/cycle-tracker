from django.db import models
from django.contrib.auth.models import User

class CycleLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    period_duration = models.IntegerField(default=5, blank=True, null=True)

    def __str__(self):
        return f"Log de {self.user.username} - {self.start_date}"

class CycleConfig(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.IntegerField()

    def __str__(self):
        return f"{self.key}: {self.value}"
