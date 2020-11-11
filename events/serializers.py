from rest_framework import serializers
from . import models

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        fields = "__all__"

class AssignmentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssignmentFile
        fields = "__all__"

class SavedAssignmentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssignmentFile
        exclude = ('assignment',)

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Assignment
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)

        assignments_files = models.AssignmentFile.objects.filter(assignment=instance.id)
        response["assignments_files"] = SavedAssignmentFileSerializer(assignments_files, many=True).data
        return response


class SubmittedAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubmittedAssignment
        fields = "__all__"

class SubmittedAssignmentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubmittedAssignmentFile
        fields = "__all__"
