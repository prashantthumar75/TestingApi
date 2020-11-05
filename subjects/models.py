from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=100)
    section = models.ForeignKey('sections.Section', blank=True, null=True, on_delete=models.SET_NULL, related_name='subject_section')
    teachers = models.ManyToManyField('teachers.Teacher', blank=True, related_name='subject_teachers')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    

    def __str__(self):
        return self.name