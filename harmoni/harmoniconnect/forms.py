from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Booking, Review, Service
from .models import CustomUser, ServiceProvider

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ServiceBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service', 'booking_date']
        widgets = {
            'booking_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
# new form code

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    service_preferences = forms.ChoiceField(choices=[
        ('event_photography', 'Event Photography'),
        ('portrait_sessions', 'Portrait Sessions'),
        ('custom_projects', 'Custom Projects')
    ], required=True)
    communication_preferences = forms.ChoiceField(choices=[
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('sms', 'SMS')
    ], required=True)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'last_name', 'email', 'service_preferences', 'communication_preferences'
        )

class ServiceProviderCreationForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(max_length=254, required=True)
    phone = forms.CharField(max_length=15, required=True)
    service_type = forms.ChoiceField(choices=[
        ('event_photography', 'Event Photography'),
        ('portrait_sessions', 'Portrait Sessions'),
        ('custom_projects', 'Custom Projects')
    ], required=True)
    tax_number = forms.CharField(max_length=100, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            'company_name', 'email', 'phone', 'service_type', 'tax_number'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_service_provider = True
        if commit:
            user.save()
            ServiceProvider.objects.create(
                user=user,
                name=self.cleaned_data['company_name'],
                location='Default Location',
                average_rating=0.0
            )
        return user
