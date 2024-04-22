from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .permissions import IsServiceProvider
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Service, ServiceProvider, Booking, Review
from .serializers import ServiceSerializer, ServiceProviderSerializer, BookingSerializer, ReviewSerializer, BookingSerializer
from django.urls import reverse_lazy
from django.views import generic
from .forms import UserRegisterForm

# ViewSets
class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow any authenticated user to view services
        if view.action in ['list', 'retrieve']:
            return request.user and request.user.is_authenticated
        
        # Only allow service providers to create, update, or delete services
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return request.user.is_authenticated and getattr(request.user, 'is_service_provider', False)

        # Default deny
        return False

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().select_related('provider')
    serializer_class = ServiceSerializer
    permission_classes = [CustomPermission]


class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.user.is_superuser:
        # Allow all actions for superusers
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only service providers can perform these actions
            permission_classes = [IsServiceProvider]
        else:
            # Any user can list or retrieve service providers
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().select_related('client', 'service')
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
            # Check if the user can specify any client (e.g., staff members)
            if 'client' in serializer.validated_data and user.is_staff:
                serializer.save()
            elif hasattr(user, 'client'):
                # For regular authenticated users who cannot specify a client
                serializer.save(client=user.client)
            else:
                # If the user does not have a client associated and is not staff
                raise PermissionDenied("You do not have permission to create a booking without a specified client.")
        else:
            # If the user is not authenticated
            raise PermissionDenied("Authentication is required to create bookings.")


    @action(detail=True, methods=['post'])
    def confirm_booking(self, request, pk=None):
        """
        Custom action to confirm a booking.
        """
        booking = self.get_object()
        if booking.client.user != request.user:
            return Response({'error': 'You do not have permission to confirm this booking'}, status=status.HTTP_403_FORBIDDEN)
        booking.status = 'confirmed'
        booking.save()
        return Response({'status': 'booking confirmed'})

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().select_related('booking')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

# Generic views for user registration and static pages
class SignUpView(generic.CreateView):
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')
