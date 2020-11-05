from django.db import models

class Class(models.Model):
    title = models.CharField(max_length=100)
    department = models.ForeignKey('departments.Department', blank=True, null=True, on_delete=models.SET_NULL, related_name='class_department')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title