from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, Patient
import re

class PatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True, label="Phone Number")
    blood_group = forms.CharField(max_length=5, required=False)
    address = forms.CharField(max_length=200, required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'blood_group',
            'password1',
            'password2'
        )

    # Username validation
    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 4:
            raise ValidationError("Username must be at least 4 characters long.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")
        return username

    # Email validation
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        return email

    # Password strength validation
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        pw_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$')  # min 6 chars, uppercase, lowercase, number
        if not pw_regex.match(password1):
            raise ValidationError("Weak password: min 6 chars, uppercase, lowercase, number.")
        return password1

    # Optional: Ensure password2 matches password1
    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get('password1')
        pw2 = cleaned_data.get('password2')
        if pw1 and pw2 and pw1 != pw2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.blood_group = self.cleaned_data.get('blood_group', '')
        user.role = 'patient'

        if commit:
            user.save()
            Patient.objects.create(
                user=user,
                contact=user.phone_number,
                address=self.cleaned_data.get('address', '')
            )
        return user
