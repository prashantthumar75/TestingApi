from django.db import models
import uuid

class Department(models.Model):
    requesting_users = models.ManyToManyField('users.User', blank=True, related_name='department_requesting_users')
    user = models.ForeignKey('users.User', blank=True, null=True, on_delete=models.CASCADE, related_name='department_user')
    name = models.CharField(max_length=100)
    department_id = models.CharField(max_length=100, blank=True, null=True)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=32, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='department_organization')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.department_id:
            temp_dept_id = str(uuid.uuid4())
            while Department.objects.filter(department_id=temp_dept_id):
                temp_dept_id = str(uuid.uuid4())
            self.department_id = temp_dept_id
        super().save(*args, **kwargs)