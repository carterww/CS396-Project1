# Generated by Django 4.1 on 2022-09-21 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fintech', '0002_post_views'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(default='', max_length=255)),
            ],
        ),
    ]