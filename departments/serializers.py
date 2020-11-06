from rest_framework import serializers
from . import models
from users import serializers as users_serializers

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)

        response["requesting_users"] = users_serializers.UserSerializer(instance.requesting_users, many=True).data

        return response
