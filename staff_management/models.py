from django.db import models
from django.core.exceptions import ValidationError

# ----------------------------
# Model for Units (departments/areas)
# ----------------------------
class Unit(models.Model):
    """Model representing a unit in the organization."""
    unit_id = models.AutoField(primary_key=True)  # Automatically incrementing unique ID
    unit_name = models.CharField(max_length=100, unique=True)  # Name of the unit, must be unique

    def __str__(self):
        return self.unit_name  # Human-readable representation in admin/UI

# ----------------------------
# Model for Weekend Groups
# ----------------------------
class WeekendGroup(models.Model):
    """Model representing a weekend group."""
    group_id = models.CharField(max_length=1, primary_key=True)  # Single-letter group ID
    group_name = models.CharField(max_length=50)  # Descriptive name of the group

    def __str__(self):
        return self.group_name

# ----------------------------
# Model for Work Shifts
# ----------------------------
class WorkShift(models.Model):
    """Model representing a work shift."""
    shift_id = models.CharField(max_length=2, primary_key=True)  # Custom ID for the shift
    shift_name = models.CharField(max_length=50)  # Descriptive shift name
    work_shift = models.CharField(max_length=10)  # Short label, like "Day", "Night"

    def __str__(self):
        return self.work_shift

# ----------------------------
# Model for Staff Members
# ----------------------------
class Staff(models.Model):
    """Model representing a staff member."""

    # Primary key
    staff_id = models.AutoField(primary_key=True)  # Automatically assigned unique ID

    # Basic personal info
    staff_name = models.CharField(max_length=100)  # Full name

    # Gender options
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=False)  # Required gender field

    # Relationships
    weekend_groups = models.ManyToManyField(WeekendGroup, blank=True)  # Staff can belong to multiple weekend groups
    work_shifts = models.ManyToManyField(WorkShift, blank=True)  # Staff can work multiple shifts
    unit_restrictions = models.ManyToManyField(Unit, blank=True)  # Units staff should NOT be assigned to
    assigned_unit = models.ManyToManyField(Unit, related_name="assigned_staff", blank=True)  # Units staff is assigned to

    # Contract type
    CONTRACT_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
    ]
    contract_type = models.CharField(max_length=10, choices=CONTRACT_TYPE_CHOICES, blank=False)  # Required field

    # Employment status
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='Active', blank=False)

    # Registration timestamp
    date_registered = models.DateTimeField(auto_now_add=True)  # Set automatically when record is created

    # Validation to prevent logical conflicts
    def clean(self):
        """
        Ensure a staff member is not assigned to a unit that they're restricted from.
        """
        super().clean()  # Run default model validation

        if self.pk:  # Only check M2M relationships if the object has been saved
            assigned_units = set(self.assigned_unit.all())
            restricted_units = set(self.unit_restrictions.all())

            # Check if any assigned units overlap with restricted units
            if assigned_units & restricted_units:
                raise ValidationError("Assigned unit(s) cannot be in unit restrictions.")

    def __str__(self):
        return f"{self.staff_name} ({self.status})"  # Friendly display for admin and debugging
