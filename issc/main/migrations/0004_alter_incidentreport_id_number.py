# Generated by Django 5.1.6 on 2025-02-11 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_accountregistration_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incidentreport',
            name='id_number',
            field=models.CharField(max_length=100),
        ),
    ]
