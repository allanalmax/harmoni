from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows login by username or email.
    """

    def authenticate(self, request, username=None, password=None):
        UserModel = get_user_model()
        if not username or not password:
            raise ValidationError('Please enter both username and password.')

        try:
            # Try finding user by username first
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            # If username not found, try by email
            try:
                validate_email(username)  # Check if username is a valid email
                user = UserModel.objects.get(email=username)
            except (UserModel.DoesNotExist, ValidationError):
                raise ValidationError('Invalid credentials. Username or email not found.')

        if not user.check_password(password):
            raise ValidationError('Invalid password.')

        return user

    def create_user(self, username, email, password):
        UserModel = get_user_model()
        if not username or not password or not email:
            raise ValueError('Please provide username, email, and password for user creation.')

        # Check for existing email before creating user
        if UserModel.objects.filter(email=email).exists():
            raise ValidationError('Email already exists.')

        user = UserModel.objects.create_user(username=username, email=email, password=password)
        return user


# class EmailOrUsernameBackend(ModelBackend):
#     """
#     Custom authentication backend that allows login by username or email.
#     """

#     def authenticate(self, request, username=None, password=None):
#         UserModel = get_user_model()
#         try:
#             # Try to find user by username
#             user = UserModel.objects.get(username=username)
#         except UserModel.DoesNotExist:
#             # If username not found, try by email
#             try:
#                 user = UserModel.objects.get(email=username)
#             except UserModel.DoesNotExist:
#                 return None
#         if user.check_password(password):
#             return user
#         return None