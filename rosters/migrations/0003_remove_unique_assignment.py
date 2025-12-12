from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rosters", "0002_shiftassignment_short_day"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="shiftassignment",
            options={"ordering": ("date",)},
        ),
    ]
