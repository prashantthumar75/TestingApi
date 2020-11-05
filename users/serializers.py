from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import gettext as _get
from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('password', 'is_active', 'groups', 'user_permissions', 'is_superuser', 'is_staff')


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
