from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .permissions import IsServiceProvider
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Service, ServiceProvider, Booking, Review
from .serializers import ServiceSerializer, ServiceProviderSerializer, BookingSerializer, ReviewSerializer, BookingSerializer
from django.urls import reverse_lazy
from .forms import UserRegisterForm, ServiceProviderCreationForm, CustomUserCreationForm
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django import forms
from django.db.models import Q
from rest_framework.test import APIRequestFactory
from django.db import IntegrityError, transaction

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
            try:
                budget_value = float(budget)
                queryset = queryset.filter(price__lte=budget_value)
            except ValueError:
                # Handle the error if the budget is not a valid number
                pass
        if start_time and end_time:
            try:
                start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
                end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S')
                booked_services = Booking.objects.filter(
                    booking_date__range=(start_time, end_time)
                ).values_list('service', flat=True)
                queryset = queryset.exclude(id__in=booked_services)
            except ValueError:
                # Handle the error if the dates are not in the correct format
                pass

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
            try:
                budget_value = float(budget)
                query &= Q(services__price__lte=budget_value)
            except ValueError:
                # Handle the error if the budget is not a valid number
                pass
        if category:
            query &= Q(services__category=category)
        if min_rating:
            try:
                min_rating_value = float(min_rating)
                query &= Q(average_rating__gte=min_rating_value)
            except ValueError:
                # Handle the error if the rating is not a valid number
                pass
        if availability_start and availability_end:
            try:
                availability_start = datetime.strptime(availability_start, '%Y-%m-%dT%H:%M:%S')
                availability_end = datetime.strptime(availability_end, '%Y-%m-%dT%H:%M:%S')
                query &= Q(services__provider__availabilities__start_time__gte=availability_start,
                           services__provider__availabilities__end_time__lte=availability_end)
            except ValueError:
                # Handle the error if the dates are not in the correct format
                pass

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

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        if self.request.user.is_service_provider:
            return reverse_lazy('provider_dashboard') 
        else:
            return reverse_lazy('home') 

class SearchTestView(TemplateView):
    template_name = 'search.html'

# def test_search(request):
#     # Simulate some search results (replace with your actual logic)
#     search_results = [
#     {'name': 'Service 1', 'description': 'Brief description', 'id': 1},  # Add an ID
#     {'name': 'Service 2', 'description': 'Another description', 'id': 2},  # Add an ID
#     ]
#     context = {'search_results': search_results}
#     return render(request, 'search.html', context)

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def customer_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                return redirect('login')
            except IntegrityError:
                form.add_error('email', 'This email is already in use.')
        else:
            print("Form is invalid")  # Debug statement
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'client_register.html', {'form': form})

def provider_register(request):
    if request.method == 'POST':
        form = ServiceProviderCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                return redirect('login')
            except IntegrityError:
                form.add_error('email', 'This email is already in use.')
        else:
            print("Form is not valid")  # Debug statement
            print(form.errors)  # Print form errors to console for debugging
    else:
        form = ServiceProviderCreationForm()
    return render(request, 'provider_register.html', {'form': form})

def search(request):
    """
    Handles search requests for service providers based on user input.
    """

    # Capture search criteria from request parameters
    category = request.GET.get('category')
    budget = request.GET.get('budget')
    availability_start = request.GET.get('start_time')
    availability_end = request.GET.get('end_time')

    # Initialize search results
    search_results = None

    if category or budget or availability_start or availability_end:
        # Use ServiceSearchViewSet for complex filtering logic
        search_results = ServiceSearchViewSet.as_view({'get': 'list'})(request).data

    # Fetch Popular or Featured Providers (modify based on your logic)
    popular_providers = ServiceProvider.objects.filter(is_featured=True)[:3]  # Assuming a boolean 'is_featured' field

    context = {'search_results': search_results, 'popular_providers': popular_providers}

    return render(request, 'search.html', context)

@login_required
def service_detail(request, service_provider_id):
    service_provider = get_object_or_404(ServiceProvider, id=service_provider_id)
    context = {'service_provider': service_provider}
    return render(request, 'service_detail.html', context)

@login_required
def provider_dashboard(request):
    return render(request, 'provider_dashboard.html')

def client_dashboard(request):
    user = {
        'name': 'Mary Cleveland',
        'role': 'Client',
    }
    bookings = [
        {
            'booking_id': 'D00568',
            'service': 'Singers',
            'date_time': '2nd February, 3pm',
            'location': 'Pearl Gardens',
            'provider': 'ABC Singers',
            'status': 'Completed',
            'special_request': 'Keep Time'
        }
    ]
    reviews = [
        {
            'user': 'Mary Cleveland',
            'role': 'Client',
            'rating': 4,
            'text': 'A critical article or report, as in a periodical, on a book, play, recital, or the like; critique; evaluation. The process of going over a subject again in study or recitation in order to fix it in the memory or summarize the facts.'
        },
        {
            'user': 'Mary Cleveland',
            'role': 'Client',
            'rating': 3,
            'text': 'A critical article or report, as in a periodical, on a book, play, recital, or the like; critique; evaluation. The process of going over a subject again in study or recitation in order to fix it in the memory or summarize the facts.'
        }
    ]
    context = {
        'user': user,
        'bookings': bookings,
        'reviews': reviews,
    }
    return render(request, 'client_dashboard.html', context)

def support(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject', 'No Subject')
        message = request.POST.get('message')

        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        send_mail(
            subject,
            full_message,
            'from@example.com',  # Replace with your email
            ['harmone@support.ac.ug'],
        )

        return HttpResponse('Thank you for your message.')

    return render(request, 'support.html')

def logout(request):
    return render(request, 'logout.html')
def booking_success(request):
    return render(request, 'booking_success.html')

def provider_dashboard(request):
    return render(request, 'provider_dashboard.html')

def reviews(request):
  
    return render(request, 'reviews.html')