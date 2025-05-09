# Generated by Django 5.1.6 on 2025-02-12 15:09

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_remove_incidentreport_date_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="FacesEmbeddings",
            fields=[
                (
                    "face_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("embedding", models.TextField()),
                ("image_hash", models.CharField(max_length=64, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id_number",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        to_field="id_number",
                    ),
                ),
            ],
        ),
    ]
