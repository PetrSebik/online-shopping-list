from django.db import models

class PriorityItem(models.Model):
    task_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority_level = models.PositiveIntegerField(default=5)
    attachment = models.FileField(upload_to='construction_docs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority_level', 'task_name']

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