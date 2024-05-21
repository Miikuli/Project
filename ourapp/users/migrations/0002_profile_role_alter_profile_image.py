# Generated by Django 5.0.6 on 2024-05-20 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('Admin', 'Admin'), ('Student', 'Student'), ('Teacher', 'Teacher')], default='Student', max_length=10),
        ),
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='user_photos/'),
        ),
    ]
