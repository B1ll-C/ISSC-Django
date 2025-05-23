# Generated by Django 5.1.6 on 2025-02-19 10:46

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0014_vehicleregistration_is_archived_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="VehicleEntry",
            fields=[
                (
                    "entry_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("is_registered", models.BooleanField(default=True)),
                ("entry_timestamp", models.DateTimeField(auto_now_add=True)),
                ("exit_timestamp", models.DateTimeField(blank=True, null=True)),
                ("entry_gate", models.CharField(max_length=100)),
                ("exit_gate", models.CharField(blank=True, max_length=100, null=True)),
                ("qr_code_scanned", models.BooleanField(default=False)),
                ("is_exited", models.BooleanField(default=False)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("last_updated_by", models.CharField(max_length=100)),
                (
                    "vehicle",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="entries",
                        to="main.vehicleregistration",
                    ),
                ),
            ],
            options={
                "verbose_name": "Vehicle Entry",
                "verbose_name_plural": "Vehicle Entries",
            },
        ),
    ]
