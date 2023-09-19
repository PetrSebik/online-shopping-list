from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return self.name
