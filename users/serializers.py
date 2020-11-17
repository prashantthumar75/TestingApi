from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import gettext as _get
from users.models import User
from django.db.models import Q
from organizations import models as organizations_models
from organizations import serializers as organizations_serializers
from departments import models as departments_models
from teachers import models as teachers_models
from students import models as student_models


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('password', 'is_active', 'groups', 'user_permissions', 'is_superuser', 'is_staff')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        qs = organizations_models.Organization.objects.filter(is_active=True)

        organization_users = qs.filter(user__id=instance.id)
        department_users = departments_models.Department.objects.filter(Q(user__id=instance.id) & Q(is_active=True))
        teacher_users = teachers_models.Teacher.objects.filter(Q(user__id=instance.id) & Q(is_active=True))
        student_users = student_models.Student.objects.filter(Q(user__id=instance.id) & Q(is_active=True))


        organizations = {}

        for _ in organization_users:
            organizations.update({
                "org": organizations_serializers.OrganizationSerializer(_).data
            })

        for _ in department_users:
            organizations.update({
                "department": organizations_serializers.OrganizationSerializer(_.organization).data
            })
        
        for _ in teacher_users:
            organizations.update({
                "teacher": organizations_serializers.OrganizationSerializer(_.organization).data
            })

        for _ in student_users:
            organizations.update({
                "student": organizations_serializers.OrganizationSerializer(_.section.of_class.department.organization).data
            })

        response["organizations"] = organizations
        return response


class TokenSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Token
        fields = ('key', 'user')


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password_reset_form_class = PasswordResetForm

    def validate_email(self, value):
        self.reset_form = self.password_reset_form_class(
            data=self.initial_data)

        if not self.reset_form.is_valid():
            raise serializers.ValidationError(
                _get('Incorrect information provided'))

        if not User.objects.filter(email=value).exists():

            raise serializers.ValidationError(
                _get('This e-mail address does not exists'))
        return value

    def save(self):
        request = self.context.get('request')
        opts = {
            'use_https': request.is_secure(),
            'from_email': "someone@gmail.com",
            'email_template_name': 'email_templates/reset_password.html',
            'html_email_template_name': 'email_templates/reset_password.html',
            'request': request,
            'extra_email_context': {'user': User.objects.get(email=self.data.get('email'))}
        }
        self.reset_form.save(**opts)
