from django.db import models
from django.contrib.auth.models import AbstractUser

PROVIDER_TYPE_CHOICES = (
    ('email', 'email'),
    ('google', 'google'),
    ('facebook', 'facebook'),
)

class User(AbstractUser):
    provider = models.CharField(max_length=20, choices=PROVIDER_TYPE_CHOICES, default='email')

    def __str__(self):
        return f"{self.username}"
