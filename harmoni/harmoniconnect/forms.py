from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Booking, Review, Service, CustomUser, ServiceProvider

User = get_user_model()

# class UserRegisterForm(UserCreationForm):
#     email = forms.EmailField(required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if User.objects.filter(email=email).exists():
#             raise ValidationError("A user with this email already exists.")
#         return email

# class ServiceBookingForm(forms.ModelForm):
#     class Meta:
#         model = Booking
#         fields = ['service', 'booking_date']
#         widgets = {
#             'booking_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
#             'service': forms.Select(attrs={'class': 'form-control'}),
#         }

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

class CustomUserCreationForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    email = forms.EmailField(max_length=254, required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        username = cleaned_data['username']
        email = cleaned_data['email']
        password = cleaned_data['password1']
        phone_number = cleaned_data.get('phone_number', '')  # Handle optional phone number

        # Create user object using your custom user model
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        user.is_client = True  # Set user type as client
        user.phone_number = phone_number  # Set phone number (optional)
        if commit:
            user.save()
        return user


class ServiceProviderCreationForm(UserCreationForm):
    username = forms.CharField(max_length=255, required=True)  # Updated field name
    email = forms.EmailField(max_length=254, required=True)
    phone = forms.CharField(max_length=15, required=True)
    location = forms.CharField(max_length=15, required=True)
    category = forms.ChoiceField(choices=[  # Updated field name and choices
        ('Dance', 'Dance'),
        ('Music', 'Music'),
        ('MC', 'Master of Ceremonies'),
    ], required=True)
    description = forms.CharField(required=True)  # Added new field

    class Meta:
        model = get_user_model()  # Assuming you have a custom user model
        fields = ['username', 'email', 'phone', 'location', 'category', 'description', 'password1', 'password2']  # Updated field list

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_service_provider = True
        if commit:
            user.save()
            ServiceProvider.objects.create(
                user=user,
                # Updated name field to use username
                name=self.cleaned_data['username'],
                location=self.cleaned_data['location'],
                average_rating=0.0
            )
        return user
    

class BookingForm(forms.ModelForm):
    event_time = forms.TimeField(required=True, widget=forms.TimeInput(format='%H:%M'))
    name = forms.CharField(required=True)
    contact = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    location = forms.CharField(required=True)
    service = forms.ModelChoiceField(queryset=Service.objects.all(), empty_label=None)


    class Meta:
        model = Booking
        fields = ['booking_date', 'service', 'special_request']

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        self.fields['booking_date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['service'].queryset = Service.objects.all()