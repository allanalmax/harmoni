from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg
from django.conf import settings


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Added unique email field
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_service_provider = models.BooleanField(default=False)

      # Identify if the user is a service provider
    def __str__(self):
          return self.username


class ServiceProvider(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="service_provider",
    )
    location = models.CharField(max_length=255)
    average_rating = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    name = models.CharField(max_length=255, default="Provider name")
    image_url = models.URLField(
        blank=True
    )  # Optional field for service provider image URL
    description = models.TextField(
        blank=True
    )  # Optional field for service provider description
    offers = models.TextField(
        blank=True
    )  # Field to store offered services (comma-separated or JSON format)
    pricing = models.TextField(
        blank=True
    )  # Field to store pricing information (text or JSON format)
    availability_description = models.TextField(
        blank=True
    )  # Text field for general availability info (e.g., "Weekdays 9am-5pm")
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Client(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client"
    )
    name = models.CharField(max_length=255, default="Client name")
    location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username


class Service(models.Model):
    service_categories = [
        ("Dance", "Dance"),
        ("Music", "Music"),
        ("MC", "Master of Ceremonies"),
        # Add more categories as needed
    ]
    name = models.CharField(max_length=255)
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="services"
    )
    location = models.CharField(max_length=255, default="")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=service_categories)

    def __str__(self):
        return f"{self.name} by {self.provider.username}"

    def save(self, *args, **kwargs):
        if not self.location:
            self.location = self.provider.location
        if not self.description:
            self.description = self.provider.description
        super().save(*args, **kwargs)


class Booking(models.Model):
    BOOKING_STATUS = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
    ]
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="bookings"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="service"
    )
    booking_date = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS)
    special_request = models.TextField(
        blank=True, null=True
    )  # Assuming special_request is a free text field
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255, default="000-000-0000")
    email = models.EmailField(default="default@example.com")
    location = models.CharField(max_length=255, default="Default Location")

    def __str__(self):
        return f"Booking on {self.booking_date} for {self.client.user.username}"

    def save(self, *args, **kwargs):
        if not self.contact:
            self.contact = "000-000-0000"
        if not self.email:
            self.email = "default@example.com"
        if not self.location:
            self.location = "Default Location"

        # Call super save to save the instance
        super().save(*args, **kwargs)


class Review(models.Model):
    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, related_name="review"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.booking.client.user.username} for Booking ID {self.booking.id}"


@receiver(post_save, sender=Review)
def update_provider_rating(sender, instance, **kwargs):
    """
    Update the ServiceProvider's average rating when a new review is added or updated.
    """
    provider = instance.booking.service.provider
    new_rating = Review.objects.filter(booking__service__provider=provider).aggregate(
        Avg("rating")
    )["rating__avg"]
    provider.average_rating = new_rating
    provider.save()


class Payment(models.Model):
    PAYMENT_STATUS = [
        ("processed", "Processed"),
        ("failed", "Failed"),
    ]
    PAYMENT_METHODS = [
        ("credit_card", "Credit Card"),
        ("paypal", "PayPal"),
        ("bank_transfer", "Bank Transfer"),
        ("mobile_money", "Mobile Money"),
        # Add more methods as needed
    ]
    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    method = models.CharField(max_length=50, choices=PAYMENT_METHODS)

    def __str__(self):
        return f"Payment of {self.amount} on {self.payment_date} for Booking ID {self.booking.id}"


class EventDetails(models.Model):
    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, related_name="event_details"
    )
    event_type = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    event_date = models.DateTimeField(db_index=True)

    def __str__(self):
        return f"Event on {self.event_date} at {self.location}"


class Availability(models.Model):
    provider = models.ForeignKey(
        ServiceProvider, on_delete=models.CASCADE, related_name="availabilities"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"Available from {self.start_time} to {self.end_time} for {self.provider.user.username}"

class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username}"