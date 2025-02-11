from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class AccountRegistration(AbstractUser):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    id_number = models.CharField(max_length=50, unique=True)
    contact_number = models.CharField(max_length=15)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    department = models.CharField(max_length=100)
    PRIVILEGE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    ]
    privilege = models.CharField(max_length=10, choices=PRIVILEGE_CHOICES)
    STATUS_CHOICES = [
        ('allowed', 'Allowed'),
        ('restricted', 'Restricted'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Account Registration"
        verbose_name_plural = "Account Registrations"


class VehicleRegistration(models.Model):
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30)
    id_number = models.CharField(max_length=100, unique=True)
    contact_number = models.CharField(max_length=15)
    email_address = models.EmailField(unique=True)
    role = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    model = models.CharField(max_length=50)
    plate_number = models.CharField(max_length=20, unique=True)
    sticker_number = models.CharField(max_length=20, unique=True)
    guardian_name = models.CharField(max_length=100)
    guardian_number = models.CharField(max_length=15)
    image = models.ImageField(upload_to='images/')
    drivers_license = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=[
        ('allowed', 'Allowed'),
        ('restricted', 'Restricted')
    ])
    qr_code = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.id_number

    class Meta:
        verbose_name = "Vehicle Registration"
        verbose_name_plural = "Vehicle Registrations"


class IncidentReport(models.Model):
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30)
    contact_number = models.CharField(max_length=15)
    id_number = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    incident = models.TextField()
    request_for_action = models.TextField()
    reported_by = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    file = models.FileField(upload_to='files/')
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending')
    ])

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"
