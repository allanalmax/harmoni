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
from datetime import datetime
from django.db.models import Q

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

class ServiceSearchViewSet(viewsets.ViewSet):
    """
    A ViewSet for searching services based on various criteria like category, budget, and availability.
    """

    def list(self, request):
        queryset = Service.objects.all()
        category = request.query_params.get('category', None)
        budget = request.query_params.get('budget', None)
        start_time = request.query_params.get('start_time', None)
        end_time = request.query_params.get('end_time', None)

        if category:
            queryset = queryset.filter(category=category)
        if budget:
            queryset = queryset.filter(price__lte=budget)
        if start_time and end_time:
            start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
            end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S')
            booked_services = Booking.objects.filter(
                booking_date__range=(start_time, end_time)
            ).values_list('service', flat=True)
            queryset = queryset.exclude(id__in=booked_services)

        serializer = ServiceSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='recommendations', url_name='recommendations')
    def recommendation_list(self, request):
        budget = request.query_params.get('budget', None)
        category = request.query_params.get('category', None)
        min_rating = request.query_params.get('min_rating', None)
        availability_start = request.query_params.get('availability_start', None)
        availability_end = request.query_params.get('availability_end', None)

        query = Q()
        if budget:
            query &= Q(services__price__lte=budget)
        if category:
            query &= Q(services__category=category)
        if min_rating:
            query &= Q(average_rating__gte=min_rating)
        if availability_start and availability_end:
            availability_start = datetime.strptime(availability_start, '%Y-%m-%dT%H:%M:%S')
            availability_end = datetime.strptime(availability_end, '%Y-%m-%dT%H:%M:%S')
            query &= Q(services__provider__availabilities__start_time__gte=availability_start,
                       services__provider__availabilities__end_time__lte=availability_end)

        providers = ServiceProvider.objects.filter(query).distinct()
        providers = providers.order_by('-average_rating')
        serializer = ServiceProviderSerializer(providers, many=True, context={'request': request})

        return Response(serializer.data)

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
