from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows login by username or email.
    """

    def authenticate(self, request, username=None, password=None):
        UserModel = get_user_model()
        try:
            # Try to find user by username
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            # If username not found, try by email
            try:
                user = UserModel.objects.get(email=username)
            except UserModel.DoesNotExist:
                return None
        if user.check_password(password):
            return user
        return None
