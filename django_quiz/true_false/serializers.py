from rest_framework import serializers
from . import models


class TFQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TF_Question
        fields = "__all__"
