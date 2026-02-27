from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="JurisdictionAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("fips_code", models.CharField(help_text="5-digit FIPS county/state code", max_length=10, unique=True)),
                ("state", models.CharField(help_text="2-letter state code", max_length=2)),
                ("contact_email", models.EmailField(max_length=254)),
                ("jurisdiction_type", models.CharField(
                    choices=[("COUNTY", "County"), ("CITY", "City"), ("STATE", "State"), ("TRIBAL", "Tribal")],
                    default="COUNTY",
                    max_length=10,
                )),
                ("website", models.URLField(blank=True)),
                ("status", models.CharField(
                    choices=[("PENDING", "Pending Review"), ("ACTIVE", "Active"), ("SUSPENDED", "Suspended")],
                    default="PENDING",
                    max_length=10,
                )),
                ("score_system", models.CharField(
                    choices=[
                        ("SCORE_0_100", "Numeric 0–100"),
                        ("GRADE_A_F", "Grade A–F"),
                        ("PASS_FAIL", "Pass / Fail"),
                        ("LETTER_NUMERIC", "Letter + Numeric (hybrid)"),
                    ],
                    default="SCORE_0_100",
                    max_length=20,
                )),
                ("schema_map", models.JSONField(blank=True, default=dict, help_text='e.g. {"facility_name": "restaurant_name"}')),
                ("webhook_url", models.URLField(blank=True, help_text="POST callback after batch completes")),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("api_key", models.OneToOneField(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="jurisdiction_account",
                    to="accounts.apikey",
                )),
                ("approved_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="approved_jurisdiction_accounts",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                "db_table": "submission_jurisdiction_accounts",
            },
        ),
        migrations.CreateModel(
            name="SubmissionBatch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(
                    choices=[
                        ("PENDING", "Pending"),
                        ("PROCESSING", "Processing"),
                        ("COMPLETE", "Complete"),
                        ("FAILED", "Failed"),
                    ],
                    default="PENDING",
                    max_length=12,
                )),
                ("source_format", models.CharField(
                    choices=[("JSON", "JSON"), ("CSV", "CSV")],
                    default="JSON",
                    max_length=4,
                )),
                ("total_rows", models.IntegerField(default=0)),
                ("created_count", models.IntegerField(default=0)),
                ("skipped_count", models.IntegerField(default=0)),
                ("error_count", models.IntegerField(default=0)),
                ("row_errors", models.JSONField(default=list)),
                ("raw_payload", models.JSONField(default=list, help_text="Original submitted records for reprocessing")),
                ("webhook_delivered", models.BooleanField(default=False)),
                ("webhook_delivered_at", models.DateTimeField(blank=True, null=True)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("jurisdiction", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="batches",
                    to="submissions.jurisdictionaccount",
                )),
            ],
            options={
                "db_table": "submission_batches",
                "ordering": ["-submitted_at"],
            },
        ),
        migrations.AddIndex(
            model_name="jurisdictionaccount",
            index=models.Index(fields=["state", "status"], name="submission__state_status_idx"),
        ),
        migrations.AddIndex(
            model_name="submissionbatch",
            index=models.Index(fields=["jurisdiction", "status"], name="submission__batch_jur_status_idx"),
        ),
    ]
