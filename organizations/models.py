from django.db import models
import uuid


class Organization(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='organization_user')
    name = models.CharField(max_length=100, blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    org_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    join_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=32, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    accepting_req = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.org_id:
            temp_org_id = str(uuid.uuid4())
            while Organization.objects.filter(org_id=temp_org_id):
                temp_org_id = str(uuid.uuid4())
            self.org_id = temp_org_id

        if not self.join_id:
            temp_join_id = str(uuid.uuid4())
            while Organization.objects.filter(join_id=temp_join_id):
                temp_join_id = str(uuid.uuid4())
            self.join_id = temp_join_id
        super().save(*args, **kwargs)