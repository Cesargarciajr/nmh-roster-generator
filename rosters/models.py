from __future__ import annotations

from django.db import models


class Roster(models.Model):
    """Simple generated roster metadata."""
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-start_date",)

    def __str__(self) -> str:
        return f"Roster {self.start_date}→{self.end_date}"


class ShiftAssignment(models.Model):
    """Assignment of a staff to a date and shift group."""
    roster = models.ForeignKey(Roster, on_delete=models.CASCADE, related_name="assignments")
    date = models.DateField(db_index=True)
    staff = models.ForeignKey("staff_management.Staff", on_delete=models.CASCADE)
    shift_group = models.ForeignKey("staff_management.ShiftGroup", on_delete=models.CASCADE)
    short_day = models.BooleanField(default=False)

    class Meta:
        # allow multiple assignments per (date, shift_group) to support capacity
        ordering = ("date",)

    def __str__(self) -> str:
        return f"{self.date} {self.shift_group} → {self.staff}"


class RosterConfig(models.Model):
    """Singleton-ish model to store roster generation settings editable by admin."""
    overbook_threshold = models.PositiveSmallIntegerField(default=6, help_text="Max allowed approved timeoff requests per date before marking it overbooked")

    class Meta:
        verbose_name = "Roster configuration"

    def clean(self):
        # prevent creating more than one config row
        from django.core.exceptions import ValidationError
        if RosterConfig.objects.exists() and (self.pk is None or not RosterConfig.objects.filter(pk=self.pk).exists()):
            raise ValidationError("A RosterConfig already exists. Edit the existing configuration instead of creating a new one.")

    def save(self, *args, **kwargs):
        # enforce singleton via clean
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls) -> "RosterConfig":
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj

    def __str__(self) -> str:
        return f"Roster config (threshold={self.overbook_threshold})"
