from django.db import models

EVENT_TYPES = [
    ("RC", 'RC'), # Regular Classes
    ("QZ", 'QZ'), # Quizz
    ("AS", 'AS'), # Assignment
]

class Event(models.Model):
    type = models.CharField(max_length=2, choices=EVENT_TYPES, default='RC')
    data = models.TextField()
    date = models.DateTimeField(blank=True, null=True)
    subject = models.ForeignKey('subjects.Subject', blank=True, null=True, on_delete=models.SET_NULL, related_name='subject_subject')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.type


class Assignment(models.Model):
    title = models.CharField(max_length=100)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='assignment_event')
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class AssignmentFile(models.Model):
    assignment = models.ForeignKey('events.Assignment', on_delete=models.CASCADE, related_name='assignmentfiles_assignment')
    file = models.FileField(upload_to='assignments/files/')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class SubmittedAssignment(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='submittedassignment_student')
    assignment = models.ForeignKey('events.Assignment', on_delete=models.CASCADE, related_name='submittedassignment_assignment')
    submitted_at = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.student.name


class SubmittedAssignmentFile(models.Model):
    submission = models.ForeignKey('events.SubmittedAssignment', on_delete=models.CASCADE, related_name='submittedassignmentfile_submission')
    file = models.FileField(upload_to='assignments/submissions/')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
