from django.db import models

class Teacher(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='teacher_user')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=32, blank=True, null=True)
    teacher_id = models.CharField(max_length=100, blank=True, null=True)
    class_teacher = models.ForeignKey('classes.Class', blank=True, null=True, on_delete= models.SET_NULL, related_name='class_teacher')
    organization = models.ForeignKey('organizations.Organization', blank=True, null=True, on_delete=models.SET_NULL, related_name='teacher_organization')
    requested_organization = models.ForeignKey('organizations.Organization', blank=True, null=True, on_delete=models.SET_NULL, related_name="teacher_requested_organization")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name