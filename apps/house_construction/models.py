import os
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


class PriorityItem(models.Model):
    task_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority_level = models.PositiveIntegerField(default=5)
    attachment = models.FileField(upload_to="construction_docs/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-priority_level", "task_name"]

    def __str__(self):
        return f"({self.priority_level}) {self.task_name}"


class ConstructionQA(models.Model):
    question = models.CharField(max_length=500)
    answer = models.CharField(max_length=500, null=True, blank=True)
    date_asked = models.DateField(auto_now_add=True)

    @property
    def is_resolved(self):
        return bool(self.answer and self.answer.strip())

    def __str__(self):
        return self.question


@receiver(post_delete, sender=PriorityItem)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.attachment:
        if os.path.isfile(instance.attachment.path):
            os.remove(instance.attachment.path)


@receiver(pre_save, sender=PriorityItem)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = PriorityItem.objects.get(pk=instance.pk).attachment
    except PriorityItem.DoesNotExist:
        return False

    new_file = instance.attachment
    if not old_file == new_file:
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)
