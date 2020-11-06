from rest_framework import serializers
from . import models

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Class
        fields = "__all__"


