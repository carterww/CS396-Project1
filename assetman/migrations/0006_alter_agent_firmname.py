# Generated by Django 4.1 on 2022-10-28 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assetman', '0005_alter_trade_fk_agent_trade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='firmName',
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]
