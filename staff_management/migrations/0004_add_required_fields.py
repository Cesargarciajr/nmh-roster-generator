from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("staff_management", "0003_staff_fixed_shift_group_staff_short_day_weekday"),
    ]

    operations = [
        migrations.AddField(
            model_name="shiftgroup",
            name="required_weekday",
            field=models.PositiveSmallIntegerField(default=1, help_text="Required staff count on weekdays"),
        ),
        migrations.AddField(
            model_name="shiftgroup",
            name="required_weekend",
            field=models.PositiveSmallIntegerField(default=0, help_text="Required staff count on weekends/bank holidays"),
        ),
    ]
