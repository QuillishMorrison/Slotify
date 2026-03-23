from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Schedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("timezone", models.CharField(default="UTC", max_length=64)),
                ("slot_size_minutes", models.PositiveIntegerField(default=30)),
                ("min_slot_size_minutes", models.PositiveIntegerField(default=15)),
                ("allow_overbooking", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["name", "id"]},
        ),
        migrations.CreateModel(
            name="AvailabilityRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("weekday", models.IntegerField(choices=[(0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday")])),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("label", models.CharField(blank=True, max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("schedule", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="availability_rules", to="slotify_django.schedule")),
            ],
            options={"ordering": ["schedule", "weekday", "start_time", "end_time"], "verbose_name": "Availability rule", "verbose_name_plural": "Availability rules"},
        ),
        migrations.CreateModel(
            name="ScheduleEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(choices=[("work", "Work"), ("busy", "Busy"), ("lunch", "Lunch"), ("break", "Break"), ("block", "Block")], max_length=64)),
                ("title", models.CharField(blank=True, max_length=255)),
                ("start", models.DateTimeField()),
                ("end", models.DateTimeField()),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("tags", models.JSONField(blank=True, default=list)),
                ("blocks_availability", models.BooleanField(default=True)),
                ("is_cancelled", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("schedule", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="events", to="slotify_django.schedule")),
            ],
            options={"ordering": ["schedule", "start", "end", "id"], "verbose_name": "Schedule event", "verbose_name_plural": "Schedule events"},
        ),
    ]
