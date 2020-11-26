from rest_framework import serializers
from . import models


class EssayQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Essay_Question
        fields = "__all__"