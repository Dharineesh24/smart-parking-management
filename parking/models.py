from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Vehicle(models.Model):

    STATUS_CHOICES = (
        ("Parked", "Parked"),
        ("Exited", "Exited"),
    )

    owner_name = models.CharField(max_length=100)
    entered_by = models.ForeignKey(User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="entered_vehicles")
    
    exited_by = models.ForeignKey(User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="exited_vehicles")

    vehicle_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    parking_slot = models.CharField(max_length=20)

    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)

    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Parked"
    )

    qr_code = models.ImageField(upload_to="qrcodes/", blank=True, null=True)
    barcode = models.ImageField(upload_to="barcodes/", blank=True, null=True)

    language = models.CharField(max_length=10, default="en")

    def __str__(self):
        return self.vehicle_number


class ParkingSetup(models.Model):

    parking_name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField()
    one_day_fee = models.PositiveIntegerField(default=20)

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("ta", "Tamil"),
    ]

    default_language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="en"
    )

    parking_logo = models.ImageField(
        upload_to="parking_logo/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.parking_name