from django.db import models
from decimal import Decimal
import uuid

class ClockifySettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_key = models.CharField(max_length=100)
    workspace_id = models.CharField(max_length=50)
    user_id = models.CharField(max_length=50)
    hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('7.5'))

    def __str__(self):
        return f"Clockify Settings {self.id} for user {self.user_id}"