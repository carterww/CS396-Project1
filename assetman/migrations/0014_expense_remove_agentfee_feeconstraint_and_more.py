# Generated by Django 4.1 on 2022-11-24 02:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assetman', '0013_alter_fintechuser_fk_address_assetuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11)),
                ('category', models.CharField(default='misc', max_length=255, null=True)),
                ('date', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='agentfee',
            name='feeConstraint',
        ),
        migrations.RemoveField(
            model_name='agentfee',
            name='feeType',
        ),
        migrations.AddField(
            model_name='fintechuser',
            name='yearly_income',
            field=models.DecimalField(decimal_places=2, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='expense',
            name='FK_user_expense',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
