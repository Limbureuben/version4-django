from unicodedata import category
from django.db import models
from datetime import date
import uuid
from django.contrib.auth.models import AbstractUser
from pyexpat import model
from django.contrib.auth.models import User
from django.forms import ValidationError



    
class Files(models.Model):
    file = models.FileField(upload_to="uploads/", null=True, blank=True)

class Category(models.Model):
    name = models.CharField(max_length=55)

class Event(models.Model):
    event_username = models.CharField(max_length=255)
    event_name = models.CharField(max_length=255)
    event_date = models.DateField(default=date.today)
    event_location = models.CharField(max_length=255)
    # event_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events', null=True)  # Link to Category
    event_category = models.CharField(max_length=100, null=False, default='default_category')
    # image = models.ImageField(upload_to='event_image/', null=True, blank=True)
    
    def __str__(self):
        return self.event_name

class EventApplication(models.Model):
    application_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=[("Attendee", "Attendee"), ("Speaker", "Speaker"), ("interested", "Interested")])
    event = models.ForeignKey(Event, related_name='applications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.event.event_name}"
    
class RegisterBook(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    publication_date = models.DateField(auto_now=True)
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    is_email_verified = models.BooleanField(default=False)  # Track if email is verified

    def __str__(self):
        return f"{self.user.username} Profile"



class Room(models.Model):
    # Define the room names as a list of choices
    SELECT_ROOM = [
        ('Small', 'Room 43'),
        ('Medium', 'Room 45'),
        ('Large', 'Room 76'),
        ('Small-medium', 'Room 14'),
        ('Medium-large', 'Room 38'),
        ('Large 68', 'Room 68'),
    ]

    # Room types (small, medium, large) based on capacity ranges
    ROOM_TYPE = [
        ('Small', 'Small Room (1-20 people)'),
        ('Small 2 ', 'Small Room (21-50 people)'),
        ('Medium', ' Medium Room (51-100 people)'),
        ('Medium 2', 'Medium Room (101-150 people)'),
        ('Large ', 'Large Room (151-200 people)'),
        ('Large 2', 'Large Room (201-300 people)'),
    ]

    # Room attributes
    name = models.CharField(
        max_length=10,
        choices=ROOM_TYPE,
        unique=True  # Ensure each room can only be registered once
    )
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE)
    capacity = models.IntegerField()  # Room's capacity in terms of people
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Room's price per hour
    location = models.CharField(max_length=255)  # Location of the room
    description = models.TextField()  # Room description
    is_available = models.BooleanField(default=True)  # Availability status
    is_requested = models.BooleanField(default=False)  # Whether the room is requested
    image = models.ImageField(upload_to='room_images/', null=True, blank=True)

    def clean(self):
        # Validation checks to ensure all fields are valid
        if not self.name:
            raise ValidationError("Room name is required.")
        if not self.room_type:
            raise ValidationError("Room type is required.")
        if self.capacity <= 0:
            raise ValidationError("Capacity must be greater than zero.")
        if self.price <= 0:
            raise ValidationError("Price must be greater than zero.")
        if not self.location:
            raise ValidationError("Location is required.")
        if not self.description:
            raise ValidationError("Description is required.")

    def __str__(self):
        # Change this to only show the name and room type
        return f"{self.get_name_display()}"
    
    

class RoomBooking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    event_name = models.CharField(max_length=255)
    number_of_attendees = models.IntegerField()
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        
        ##automatically calculate the price
        if not self.total_price:
            hours = (self.end_time.hour - self.start_time.hour) + \
                    (self.end_time.minute - self.start_time.minute ) / 60.0
            self.total_price = self.room.price_per_hour * hours
        super().save(*args, **kwargs)
            

class Invoice(models.Model):
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('canceled', 'Canceled'),
    ]
    
    
    
    