from django.db import models
import uuid


class Student(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='student_user')
    name = models.CharField(max_length=120)
    student_id = models.CharField(max_length=120, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    requested_section = models.ForeignKey('sections.Section', blank=True, null=True, on_delete=models.SET_NULL, related_name="student_requested_section")
    section = models.ForeignKey('sections.Section', blank=True, null=True, on_delete=models.SET_NULL, related_name='student_section')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.student_id:
            temp_stud_id = str(uuid.uuid4())
            while Student.objects.filter(student_id=temp_stud_id):
                temp_stud_id = str(uuid.uuid4())
            self.student_id = temp_stud_id
        super().save()