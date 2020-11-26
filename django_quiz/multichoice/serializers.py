from rest_framework import serializers
from . import models


class MCQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MCQuestion
        fields = "__all__"


class AnswerofSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Answer
        fields = "__all__"

