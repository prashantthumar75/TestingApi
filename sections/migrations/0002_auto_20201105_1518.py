# Generated by Django 3.1.2 on 2020-11-05 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classes', '0002_class_department'),
        ('teachers', '0001_initial'),
        ('sections', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='class_teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='section_class_teacher', to='teachers.teacher'),
        ),
        migrations.AddField(
            model_name='section',
            name='of_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='section_of_class', to='classes.class'),
        ),
    ]