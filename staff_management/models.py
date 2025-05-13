from django.db import models

class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    staff_name = models.CharField(max_length=100)

    # Gender (Choices: Male, Female)
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=False) 

     # Weekend Group (Choices: 1–4)
    WEEKEND_GROUP_CHOICES = [
        ('1', 'Weekend Group 1'),
        ('2', 'Weekend Group 2'),
        ('3', 'Weekend Group 3'),
        ('4', 'Weekend Group 4'),
    ]

    weekend_group = models.CharField(max_length=1, choices=WEEKEND_GROUP_CHOICES, blank=False)

     # Shift Period Assigned (Choices: D1, D2, D3, E, N)
    SHIFT_PERIOD_CHOICES = [
        ('D1', 'Shift Period D1'),
        ('D2', 'Shift Period D2'),
        ('D3', 'Shift Period D3'),
        ('E', 'Shift Period E'),
        ('N', 'Shift Period N'),
    ]
    shift_period_assigned = models.CharField(
        max_length=2, choices=SHIFT_PERIOD_CHOICES, blank=False
    )
    
    # Unit Restrictions (Optional field, specify what type it is - text or code)
    unit_restrictions = models.TextField(blank=True, null=True)

    # Assigned Unit (Optional field, specify unit name)
    assigned_unit = models.CharField(max_length=255, blank=True, null=True)

    # Contract Type (Choices: Full-time, Part-time)
    CONTRACT_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
    ]

    contract_type = models.CharField(max_length=10, choices=CONTRACT_TYPE_CHOICES, blank=False)

    # Status (Default to 'Active')
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Suspended', 'Suspended'),
    ]

    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='Active', blank=False)

     # Date of registration
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff_name} ({self.status})"
