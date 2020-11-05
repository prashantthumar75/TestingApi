from django.db import models

class Organization(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='organization_user')
    name = models.CharField(max_length=100, blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    join_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=32, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    accepting_req = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name