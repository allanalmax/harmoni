import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsServiceProvider
from .models import (
    Service,
    ServiceProvider,
    Booking,
    Review,
    Availability,  # noqa: F401
    Client,
    Notification,
)  # noqa: F401
from .serializers import (
    ServiceSerializer,
    ServiceProviderSerializer,
    BookingSerializer,  # noqa: F401
    ReviewSerializer,
)
from django.urls import reverse_lazy, reverse
from .forms import ServiceProviderCreationForm, CustomUserCreationForm, BookingForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.db import IntegrityError, transaction
import logging


# ViewSets
class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow any authenticated user to view services
        if view.action in ["list", "retrieve"]:
            return request.user and request.user.is_authenticated

        # Only allow service providers to create, update, or delete services
        if view.action in ["create", "update", "partial_update", "destroy"]:
            return request.user.is_authenticated and getattr(
                request.user, "is_service_provider", False
            )

        # Default deny
        return False


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().select_related("provider")
    serializer_class = ServiceSerializer
    permission_classes = [CustomPermission]


class ServiceSearchViewSet(viewsets.ViewSet):
    """
    A ViewSet for searching services based on various criteria like category, budget, and availability.
    """

    def list(self, request):
        queryset = Service.objects.all()
        category = request.query_params.get("category", None)
        budget = request.query_params.get("budget", None)
        start_time = request.query_params.get("start_time", None)
        end_time = request.query_params.get("end_time", None)

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
                start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
                end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")
                # Filter services based on availability that overlaps with the specified time range
                queryset = queryset.filter(
                    provider__availabilities__start_time__lte=end_time,
                    provider__availabilities__end_time__gte=start_time,
                )
            except ValueError:
                # Handle the error if the dates are not in the correct format
                pass

        serializer = ServiceSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="recommendations",
        url_name="recommendations",
    )
    def recommendation_list(self, request):
        budget = request.query_params.get("budget", None)
        category = request.query_params.get("category", None)
        min_rating = request.query_params.get("min_rating", None)
        availability_start = request.query_params.get("availability_start", None)
        availability_end = request.query_params.get("availability_end", None)

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
                availability_start = datetime.strptime(
                    availability_start, "%Y-%m-%dT%H:%M:%S"
                )
                availability_end = datetime.strptime(
                    availability_end, "%Y-%m-%dT%H:%M:%S"
                )
                # Filter providers based on availability that overlaps with the specified time range
                query &= Q(
                    availabilities__start_time__lte=availability_end,
                    availabilities__end_time__gte=availability_start,
                )
            except ValueError:
                # Handle the error if the dates are not in the correct format
                pass

        providers = ServiceProvider.objects.filter(query).distinct()
        providers = providers.order_by("-average_rating")
        serializer = ServiceProviderSerializer(
            providers, many=True, context={"request": request}
        )

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
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            # Only service providers can perform these actions
            permission_classes = [IsServiceProvider]
        else:
            # Any user can list or retrieve service providers
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# class BookingViewSet(viewsets.ModelViewSet):
#     queryset = Booking.objects.all().select_related('client', 'service')
#     serializer_class = BookingSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         user = self.request.user
#         if user.is_authenticated:
#             # Check if the user can specify any client (e.g., staff members)
#             if 'client' in serializer.validated_data and user.is_staff:
#                 serializer.save()
#             elif hasattr(user, 'client'):
#                 # For regular authenticated users who cannot specify a client
#                 serializer.save(client=user.client)
#             else:
#                 # If the user does not have a client associated and is not staff
#                 raise PermissionDenied("You do not have permission to create a booking without a specified client.")
#         else:
#             # If the user is not authenticated
#             raise PermissionDenied("Authentication is required to create bookings.")


#     @action(detail=True, methods=['post'])
#     def confirm_booking(self, request, pk=None):
#         """
#         Custom action to confirm a booking.
#         """
#         booking = self.get_object()
#         if booking.client.user != request.user:
#             return Response({'error': 'You do not have permission to confirm this booking'}, status=status.HTTP_403_FORBIDDEN)
#         booking.status = 'confirmed'
#         booking.save()
#         return Response({'status': 'booking confirmed'})


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().select_related("booking")
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]



# Generic views for user registration and static pages
# class SignUpView(generic.CreateView):
#     form_class = UserRegisterForm
#     success_url = reverse_lazy('login')
#     template_name = 'registration/signup.html'


class CustomLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        if self.request.user.is_service_provider:
            return reverse_lazy("provider_dashboard")
        else:
            return reverse_lazy("home")


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


@csrf_protect
# def login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             auth_login(request, user)
#             if hasattr(user, 'serviceprovider'):
#                 return redirect('provider_dashboard', service_provider_id=user.serviceprovider.id)
#             else:
#                 return redirect('client_dashboard')
#         else:
#             error_message = "Invalid username or password."
#             return render(request, 'registration/login.html', {'error_message': error_message})
#     return render(request, 'login.html')

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            # It's better using this method. it will reduce the if condition statements if you are to check theuser is-service provider
            if hasattr(
                user, "service_provider"
            ):  # Check if the user is a service provider.
                try:
                    service_provider_id = user.service_provider.id
                    dashboard_url = reverse(
                        "provider_dashboard",
                        kwargs={"service_provider_id": service_provider_id},
                    )
                    return redirect(dashboard_url)
                except ServiceProvider.DoesNotExist:
                    return render(
                        request,
                        "login.html",
                        {"error_message": "Service provider does not exist"},
                    )
            else:
                return redirect(
                    "client_dashboard"
                )  # Redirect to client dashboard for non-service providers
        else:
            return render(
                request, "login.html", {"error_message": "Invalid username or password"}
            )
    else:
        return render(request, "login.html")


def register(request):
    return render(request, "register.html")


def customer_register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                return redirect("login")
            except IntegrityError:
                form.add_error("email", "This email is already in use.")
        else:
            print("Form is invalid")  # Debug statement
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, "client_register.html", {"form": form})


def provider_register(request):
    if request.method == "POST":
        form = ServiceProviderCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                return redirect("login")
            except IntegrityError:
                form.add_error("email", "This email is already in use.")
        else:
            print("Form is not valid")  # Debug statement
            print(form.errors)  # Print form errors to console for debugging
    else:
        form = ServiceProviderCreationForm()
    return render(request, "provider_register.html", {"form": form})


@login_required
def provider_dashboard(request, service_provider_id):
    service_provider = get_object_or_404(ServiceProvider, id=service_provider_id)

    # Get all services provided by the service provider
    services = Service.objects.filter(provider=service_provider.id)

    # Filter bookings by these services
    pending_bookings = Booking.objects.filter(service__in=services, status="pending")
    scheduled_bookings = Booking.objects.filter(
        service__in=services, status="confirmed"
    )
    completed_bookings = Booking.objects.filter(
        service__in=services, status="completed"
    )

    print(f"Pending Bookings: {pending_bookings}")
    print(f"Scheduled Bookings: {scheduled_bookings}")
    print(f"Completed Bookings: {completed_bookings}")

    context = {
        "service_provider": service_provider,
        "service_provider_id": service_provider.id,
        "pending_bookings": pending_bookings,
        "scheduled_bookings": scheduled_bookings,
        "completed_bookings": completed_bookings,
    }
    return render(request, "provider_dashboard.html", context)


@login_required
def client_dashboard(request):
    client = get_object_or_404(Client, user=request.user)
    scheduled_bookings = Booking.objects.filter(
        client=client, status__in=["pending", "confirmed"]
    )
    completed_bookings = Booking.objects.filter(client=client, status="completed")
    # This is what you missed in your code to fetch reviews.
    reviews = Review.objects.filter(  # noqa: F841
        booking__client=client
    )  # Assuming you want to fetch reviews for the client

    if request.method == "POST":
        action = request.POST.get("action")
        booking_id = request.POST.get(
            "booking_id"
        )  # Assuming how booking ID is passed in your template

        if action == "cancel_booking":
            booking = get_object_or_404(Booking, id=booking_id)
            booking.delete()
            return redirect(
                "client_dashboard"
            )  # Redirect to the client dashboard after cancellation

        elif action == "proceed_to_payment":
            booking = get_object_or_404(Booking, id=booking_id)
            # Handle payment processing logic here
            return HttpResponse("Proceed to payment logic goes here")

    context = {
        "client": client,
        "scheduled_bookings": scheduled_bookings,
        "completed_bookings": completed_bookings,
    }
    return render(request, "client_dashboard.html", context)


def search(request):
    # Capture search criteria from request parameters
    category = request.GET.get("category")
    start_time = request.GET.get("start_time")
    end_time = request.GET.get("end_time")

    # Initialize search results
    search_results = None
    provider_query = None

    if category or (start_time and end_time):
        if category:
            try:
                service_query = Service.objects.filter(category=category)

                provider_ids = service_query.values_list(
                    "provider_id", flat=True
                ).distinct()

                provider_query = ServiceProvider.objects.filter(
                    id__in=provider_ids
                ).distinct()

                if not provider_query.exists():
                    return render(
                        request,
                        "search.html",
                        {
                            "error_message": "No service providers found for this category.",
                            "service_categories": Service.service_categories,
                            "search_results": search_results,
                            "popular_providers": ServiceProvider.objects.filter(
                                is_featured=True
                            )[:3],
                        },
                    )

            except Exception as e:
                return render(
                    request,
                    "search.html",
                    {
                        "error_message": f"An error occurred: {str(e)}",
                    },
                )

        if start_time and end_time:
            try:
                start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
                end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")
                availability_query = ServiceProvider.objects.filter(
                    availabilities__start_time__lte=end_time,
                    availabilities__end_time__gte=start_time,
                ).distinct()

                if search_results is not None:
                    search_results = provider_query & availability_query
                else:
                    search_results = provider_query
            except Exception as e:
                return render(
                    request,
                    "search.html",
                    {"error_message": f"Error processing availability: {str(e)}"},
                )
        if not search_results:
            search_results = provider_query.distinct()

    # Fetch Popular or Featured Providers (modify based on your logic)
    popular_providers = ServiceProvider.objects.filter(is_featured=True)[:3]

    service_categories = Service.service_categories
    print(
        f"Service Categories: {service_categories}"
    )  # Debugging line to check if categories are being set

    context = {
        "search_results": search_results,
        "popular_providers": popular_providers,
        "service_categories": Service.service_categories,
    }

    return render(request, "search.html", context)


@login_required
def service_detail(request, service_provider_id):
    service_provider = get_object_or_404(ServiceProvider, id=service_provider_id)
    service_provider = ServiceProvider.objects.get(id=service_provider_id)
    # Split plain text fields by newlines
    service_provider.offers = service_provider.offers.split("\n")
    service_provider.pricing = service_provider.pricing.split("\n")
    service_provider.availability_description = (
        service_provider.availability_description.split("\n")
    )

    context = {
        "service_provider": service_provider,
        "service_provider_id": service_provider.id,
    }
    return render(request, "service_detail.html", context)


logger = logging.getLogger(__name__)


def book_service(request, service_provider_id):
    service_provider = ServiceProvider.objects.get(user_id=service_provider_id)
    client = get_object_or_404(Client, user=request.user)
    service = get_object_or_404(Service, provider=service_provider.user)

    initial_data = {  # noqa: F841
        # "booking_date": timezone.now().date(),
        "service_name": service.name,
        "client_name": client.name,
    }

    if request.method == "POST":
        form = BookingForm(
            request.POST,
            client_name=client.name,
            service_name=service.name,
            # booking_date=timezone.now().date(),
        )
        if form.is_valid():
            logger.info("Form is valid. Proceeding to save booking...")

            booking = form.save(commit=False)
            booking.service_provider = service_provider
            # booking.client = Client.objects.get(user=request.user)
            booking.client = client
            booking.service = service

            # Combine booking_date and event_time into a single timezone-aware datetime

            booking.booking_date = timezone.make_aware(
                timezone.datetime.combine(
                    form.cleaned_data["booking_date"], form.cleaned_data["event_time"]
                )
            )
            # Save other form fields directly to the Booking instance
            booking.name = client.name
            booking.contact = form.cleaned_data["contact"]
            booking.email = form.cleaned_data["email"]
            booking.location = form.cleaned_data["location"]
            booking.status = "pending"

            logger.info(f"Booking details: {booking}")

            booking.save()
            logger.info("Booking saved successfully!")

            # Create notification for service provider
            provider_notification = Notification.objects.create(  # noqa: F841
                recipient=service_provider.user,
                message=f"You have a new booking request (ID: {booking.id}). Please check your dashboard to review and approve.",
            )
            messages.success(request, "Booking request sent successfully.")

            return redirect("booking_success", booking_id=booking.id)
        else:
            logger.error("Form is invalid")
            logger.error(form.errors)
    else:
        form = BookingForm(
            client_name=client.name,
            service_name=service.name,
            initial={
                "service_name": service.name,
                "name": client.name,
            },
        )

    context = {
        "form": form,
        "service_provider": service_provider,
        "client_name": client.name,
        "service": service,
    }

    return render(request, "book_service.html", context)


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    context = {"booking": booking}
    return render(request, "booking_success.html", context)


@login_required
@csrf_protect
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)


    if request.method == 'POST':
        # Assuming service_provider is a related field on CustomUser
        if booking.service.provider.service_provider == request.user.service_provider:
            booking.status = "confirmed"
            booking.save()

            # Create notification for client
            client_notification = Notification.objects.create(
                recipient=booking.client.user,
                message=f"Your booking (ID: {booking.id}) has been confirmed. Please Check your dashboard and proceed to payment. Thank you for booking with us!",
            )
            messages.success(request, "Booking confirmed successfully.")

            print(f"Booking ID {booking.id} confirmed by {request.user.username}")

            return redirect("provider_dashboard", service_provider_id=request.user.service_provider.id)
        else:
            print("User does not have permission to confirm this booking.")
            messages.error(request, "Permission denied to confirm this booking.")
    else:
        print("GET request received, expecting POST.")

    # Handle any errors or redirect to appropriate page if not POST or permission denied
    return redirect("provider_dashboard", service_provider_id=request.user.service_provider.id)

@login_required
@csrf_protect
def decline_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.service.provider.service_provider == request.user.service_provider:
        booking.status = "declined"  # Assuming 'declined' is a valid status
        booking.save()

        # Create notification for client
        client_notification = Notification.objects.create(  # noqa: F841
            recipient=booking.client.user,
            message=f"Your booking (ID: {booking.id}) has been declined. Explore more service providers to find the one that suits you.",
        )
        messages.success(request, "Booking declined successfully.")

    return redirect(
        "provider_dashboard", service_provider_id=request.user.service_provider.id
    )


@login_required
def complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.service.provider.service_provider == request.user.service_provider:
        booking.status = "completed"
        booking.save()

        # Create notification for client
        client_notification = Notification.objects.create(  # noqa: F841
            recipient=booking.client.user,
            message=f"Your booking (ID: {booking.id}) has been completed.",
        )
        messages.success(request, "Booking completed successfully.")

    return redirect(
        "provider_dashboard", service_provider_id=request.user.service_provider.id
    )


def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, "notify.html", {"notifications": notifications})


def mark_notification_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    if notification.recipient == request.user:
     notification.read = True
     notification.save()
    return redirect("notifications")


def reviews(request):
    return render(request, "reviews.html")


def support(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject", "No Subject")
        message = request.POST.get("message")

        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        send_mail(
            subject,
            full_message,
            "from@example.com",  # Replace with your email
            ["harmone@support.ac.ug"],
        )

        return HttpResponse("Thank you for your message.")

    return render(request, "support.html")


def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")
