# Generated by Django 4.0 on 2022-01-03 06:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0006_alter_book_book'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookRead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(default='45.243.82.169')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.book')),
            ],
        ),
    ]
