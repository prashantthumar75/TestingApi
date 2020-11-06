from rest_framework import serializers
from . import models
from departments import serializers as departments_serializers

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Class
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)

        response["department_name"] = instance.department.name
        response["department_id"] = instance.department.department_id if instance.department.department_id else ""

        return response

