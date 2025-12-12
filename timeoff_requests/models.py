# timeoff_requests/models.py
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q, F
from django.utils import timezone

STAFF_FK = "staff_management.Staff"


class RequestStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class LeaveType(models.TextChoices):
    HOLIDAY = "HOLIDAY", "Holiday / Annual Leave"
    SICK = "SICK", "Sick Leave"
    MATERNITY = "MATERNITY", "Maternity Leave"
    PATERNITY = "PATERNITY", "Paternity Leave"
    PARENTAL = "PARENTAL", "Parental Leave"
    OTHER = "OTHER", "Other"


class DatedRequest(models.Model):
    """
    Abstract base for multi-day requests (Holiday/Leave).
    Provides: staff, start/end dates, status, comment, audit trail.
    """
    staff = models.ForeignKey(STAFF_FK, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
        db_index=True,
    )
    comment = models.CharField(max_length=200, blank=True, default="")

    # Audit fields — unique reverse names per concrete subclass
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_updated",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_approved",
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ("-start_date", "-end_date", "-created_at")
        constraints = [
            models.CheckConstraint(
                check=Q(end_date__gte=F("start_date")),
                name="%(app_label)s_%(class)s_end_on_or_after_start",
            ),
        ]
        indexes = [
            models.Index(fields=["staff", "start_date"]),
            models.Index(fields=["staff", "end_date"]),
        ]

    # ----- helpers / behavior -----
    @property
    def is_pending(self) -> bool:
        return self.status == RequestStatus.PENDING

    @property
    def is_approved(self) -> bool:
        return self.status == RequestStatus.APPROVED

    @property
    def is_rejected(self) -> bool:
        return self.status == RequestStatus.REJECTED

    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days + 1

    def approve(self, by_user) -> None:
        self.status = RequestStatus.APPROVED
        self.approved_by = by_user
        self.approved_at = timezone.now()

    def reject(self, by_user) -> None:
        self.status = RequestStatus.REJECTED
        self.approved_by = by_user
        self.approved_at = timezone.now()

    def reset_to_pending(self) -> None:
        self.status = RequestStatus.PENDING
        self.approved_by = None
        self.approved_at = None

    def save(self, *args, **kwargs):
        # Keep approved_at consistent with status
        if self.status == RequestStatus.PENDING:
            self.approved_by = None
            self.approved_at = None
        elif self.status in (RequestStatus.APPROVED, RequestStatus.REJECTED) and self.approved_at is None:
            # If someone manually toggled status without using approve()/reject()
            self.approved_at = timezone.now()
        super().save(*args, **kwargs)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")

    def __str__(self) -> str:
        return f"{self.staff} {self.start_date}→{self.end_date} ({self.get_status_display()})"


class Holiday(DatedRequest):
    """Paid time off / annual leave."""
    class Meta:
        permissions = [
            ("approve_holiday", "Can approve holiday requests"),
        ]


class Leave(DatedRequest):
    """Other leave types (sick, maternity, etc.)."""
    leave_type = models.CharField(
        max_length=12,
        choices=LeaveType.choices,
        default=LeaveType.OTHER,
        db_index=True,
    )

    class Meta:
        permissions = [
            ("approve_leave", "Can approve leave requests"),
        ]

    def __str__(self) -> str:
        return f"Leave: {self.staff} {self.get_leave_type_display()} {self.start_date}→{self.end_date} ({self.get_status_display()})"


class DayOffRequest(models.Model):
    """
    Single specific day off (not a range).
    Own set of audit fields with unique reverse names.
    """
    staff = models.ForeignKey(STAFF_FK, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    status = models.CharField(
        max_length=10,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
        db_index=True,
    )
    comment = models.CharField(max_length=200, blank=True, default="")

    # Audit fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="timeoff_requests_dayoff_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="timeoff_requests_dayoff_updated",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="timeoff_requests_dayoff_approved",
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        unique_together = ("staff", "date")
        ordering = ("-date", "-created_at")
        permissions = [
            ("approve_dayoff", "Can approve day-off requests"),
        ]
        indexes = [
            models.Index(fields=["staff", "date"]),
        ]

    # ----- helpers / behavior -----
    @property
    def is_pending(self) -> bool:
        return self.status == RequestStatus.PENDING

    def approve(self, by_user) -> None:
        self.status = RequestStatus.APPROVED
        self.approved_by = by_user
        self.approved_at = timezone.now()

    def reject(self, by_user) -> None:
        self.status = RequestStatus.REJECTED
        self.approved_by = by_user
        self.approved_at = timezone.now()

    def reset_to_pending(self) -> None:
        self.status = RequestStatus.PENDING
        self.approved_by = None
        self.approved_at = None

    def save(self, *args, **kwargs):
        if self.status == RequestStatus.PENDING:
            self.approved_by = None
            self.approved_at = None
        elif self.status in (RequestStatus.APPROVED, RequestStatus.REJECTED) and self.approved_at is None:
            self.approved_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"DayOff: {self.staff} {self.date} ({self.get_status_display()})"
