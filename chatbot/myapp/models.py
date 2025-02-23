from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    USER_TYPES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='patient')
    phone = models.CharField(max_length=15)
    address = models.TextField()
    age = models.IntegerField()
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)  # For doctors
    experience = models.IntegerField(default=0)  # For doctors
    available_times = models.TextField(blank=True, null=True)  # For doctors

    def __str__(self):
        return f"{self.user.username}'s profile ({self.user_type})"

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    experience = models.IntegerField()
    available_times = models.TextField()
    contact = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    
    patient = models.ForeignKey(User, related_name='patient_appointments', on_delete=models.CASCADE, default=1)  # Provide a default value
    doctor = models.ForeignKey(User, related_name='doctor_appointments', on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)  # Changed from auto_now_add to default

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.username} for {self.patient.username}"

class Blog(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
