from rest_framework import serializers
from . import models


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Quiz
        fields = "__all__"

