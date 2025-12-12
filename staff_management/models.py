# staff_management/models.py
from __future__ import annotations
from django.conf import settings
from django.db import models
from django.utils import timezone

class Gender(models.TextChoices):
    FEMALE = "F", "Female"
    MALE = "M", "Male"
    OTHER = "O", "Other/Not specified"

class ShiftGroup(models.Model):
    shift_name = models.CharField(max_length=40, unique=True)
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=120, blank=True, default="")
    # Required number of staff for weekdays and weekends (defaults can be tuned per shift)
    required_weekday = models.PositiveSmallIntegerField(default=1, help_text="Required staff count on weekdays")
    required_weekend = models.PositiveSmallIntegerField(default=0, help_text="Required staff count on weekends/bank holidays")

    class Meta:
        ordering = ("shift_name",)

    def __str__(self) -> str:
        return self.shift_name

class WeekendGroup(models.Model):
    number = models.PositiveSmallIntegerField(
        choices=[(i, f"Week {i}") for i in range(1, 5)],
        unique=True
    )
    name = models.CharField(max_length=50, blank=True, default="")
    def __str__(self) -> str:
        return self.name or f"Weekend {self.number}"

class Staff(models.Model):
    full_name   = models.CharField(max_length=120)
    employee_id = models.CharField(max_length=50, unique=True)
    gender      = models.CharField(max_length=1, choices=Gender.choices, default=Gender.OTHER)
    active      = models.BooleanField(default=True)

    # NEW: many-to-many relation to shift groups
    shift_groups = models.ManyToManyField(
        ShiftGroup,
        related_name="staff",
        blank=True,
        help_text="All shift groups this staff can work"
    )

    can_do_weekend_morning = models.BooleanField(
        default=False,
        help_text="Evening staff may cover Morning on weekends"
    )
    must_do_weekly_evening = models.BooleanField(
        default=True,
        help_text="Morning staff should do one Evening per week"
    )

    weekend_group = models.ForeignKey(WeekendGroup, null=True, blank=True, on_delete=models.SET_NULL)

    # Optional: staff who are fixed to a particular shift group (always work this shift)
    fixed_shift_group = models.ForeignKey(
        ShiftGroup,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="fixed_staff",
        help_text="If set, this staff will be pre-assigned to this shift group when available",
    )

    # Short day: weekday index (0=Mon..6=Sun) when the staff finishes 1 hour earlier (optional)
    SHORT_DAY_CHOICES = [(i, d) for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]) ]
    short_day_weekday = models.PositiveSmallIntegerField(null=True, blank=True, choices=SHORT_DAY_CHOICES)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="staff_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="staff_updated"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.full_name} ({self.employee_id})"

