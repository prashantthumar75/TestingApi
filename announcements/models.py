from django.db import models

# Create your models here.

class Announcement(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='announcement_user')
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='announcement_organization')

    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    data = models.TextField(blank=True,null=True)
    date = models.DateTimeField(blank=True, null=True)
    visible = models.TextField(blank=True,null=True)
    From = models.TextField(blank=True,null=True)
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    acknowledge = models.BooleanField(default=False)

    def __str__(self):
        return str(self.title)

class AnnouncementFile(models.Model):
    announcement = models.ForeignKey('Announcement', on_delete=models.CASCADE, related_name='Announcementfiles')
    file = models.FileField(upload_to='announcement/files/')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
