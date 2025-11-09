from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')  # <-- important

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)
class User(AbstractUser):
    ROLE_CHOICES = [('admin','Admin'), ('doctor','Doctor'), ('patient','Patient')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False)
    is_approved = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    objects = CustomUserManager() 

# -------------------------------
# Doctor Model
# -------------------------------

# -------------------------------
# Patient Model
# -------------------------------
class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contact = models.CharField(max_length=15)
    address = models.CharField(max_length=200)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} | {self.user.blood_group or 'N/A'} | {self.age or 'N/A'} | {self.gender or 'N/A'}"

# -------------------------------
# Doctor Registration Request
# -------------------------------
from django.conf import settings
from django.db import models

# DoctorRegistrationRequest model (used for registration requests)
from django.db import models

class DoctorRegistrationRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    # Basic user info
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=20)
    blood_group = models.CharField(max_length=5)
    password = models.CharField(max_length=128)
    
    # Professional info (required)
    degree = models.CharField(max_length=150, blank=False, null=False)
    specialization = models.CharField(max_length=150, blank=True, null=True)  # optional
    experience_years = models.PositiveIntegerField(blank=True, null=True)      # optional
    bio = models.TextField(blank=True, null=True)                              # optional


    # Documents & profile picture
    identity_document = models.FileField(upload_to='doctor_ids/')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Metadata
    role = models.CharField(max_length=20, default='doctor')
    is_approved = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def profile_pic_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default_profile.png'

    def __str__(self):
        return f"{self.username} ({self.status})"



# Doctor model (for storing actual approved doctors linked to a user)
class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    identity_document = models.FileField(upload_to='doctor_ids/', blank=True, null=True)
    degree = models.CharField(max_length=150, blank=True, null=True)
    specialization = models.CharField(max_length=150, blank=True, null=True)
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    @property
    def full_name(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"

    @property
    def profile_pic_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default_profile.png'

    def __str__(self):
        return self.full_name

# -------------------------------
# Contact Message
# -------------------------------
class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} | {self.email}"

# -------------------------------
# Reply Model
# -------------------------------
class Reply(models.Model):
    message = models.ForeignKey(ContactMessage, on_delete=models.CASCADE, related_name='replies')
    subject = models.CharField(max_length=200)
    reply_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
   

    def __str__(self):
        return f"Reply to {self.message.name}"

class MessageReply(models.Model):
    parent = models.ForeignKey(ContactMessage, related_name='replies_message', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reply_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    

