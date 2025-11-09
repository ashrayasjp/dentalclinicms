from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from appointments.models import Doctor

User = get_user_model()

@receiver(post_save, sender=User)
def create_doctor_profile(sender, instance, created, **kwargs):
    # Only for new users with role='doctor'
    if created and instance.role == 'doctor':
        Doctor.objects.create(user=instance)
