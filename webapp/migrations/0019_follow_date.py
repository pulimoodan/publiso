# Generated by Django 4.0 on 2022-01-09 05:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0018_book_pages'),
    ]

    operations = [
        migrations.AddField(
            model_name='follow',
            name='date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]