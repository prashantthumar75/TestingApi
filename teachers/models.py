from django.db import models
import uuid
class Teacher(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='teacher_user')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=32, blank=True, null=True)
    teacher_id = models.CharField(max_length=100, blank=True, null=True)
    organization = models.ForeignKey('organizations.Organization', blank=True, null=True, on_delete=models.SET_NULL, related_name='teacher_organization')
    requested_organization = models.ForeignKey('organizations.Organization', blank=True, null=True, on_delete=models.SET_NULL, related_name="teacher_requested_organization")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.teacher_id:
            temp_tech_id = str(uuid.uuid4())
            while Teacher.objects.filter(teacher_id=temp_tech_id):
                temp_tech_id = str(uuid.uuid4())
            self.teacher_id = temp_tech_id
        super().save()