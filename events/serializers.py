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

        assignment_files = models.AssignmentFile.objects.filter(assignment=instance.id)
        response["assignment_files"] = SavedAssignmentFileSerializer(assignment_files, many=True).data
        return response


class SubmittedAssignmentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubmittedAssignmentFile
        fields = "__all__"

class SavedSubmittedAssignmentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubmittedAssignmentFile
        exclude = ('submission',)

class SubmittedAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubmittedAssignment
        fields = "__all__"
    
    def to_representation(self, instance):
        response = super().to_representation(instance)

        submitted_assignment_files = models.SubmittedAssignmentFile.objects.filter(submission=instance.id)
        response["submitted_assignment_files"] = SavedAssignmentFileSerializer(submitted_assignment_files, many=True).data
        return response