from django.db import models

# Create your models here.

class Announcement(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='announcement_user')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    data = models.TextField(blank=True,null=True)
    date = models.DateTimeField(blank=True, null=True)
    visible = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.title)

