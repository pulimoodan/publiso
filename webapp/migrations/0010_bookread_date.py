# Generated by Django 4.0 on 2022-01-03 09:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0009_follow'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookread',
            name='date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
