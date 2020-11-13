from rest_framework import serializers
from . import models


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Announcement
        fields = "__all__"

