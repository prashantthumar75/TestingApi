# Generated by Django 3.1.2 on 2020-11-05 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_organization_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='organization',
            old_name='uuid',
            new_name='org_id',
        ),
    ]