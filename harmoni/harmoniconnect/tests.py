from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import ServiceProvider, Service, Client
from decimal import Decimal
from django.utils.timezone import now, timedelta

User = get_user_model()

# class ServiceProviderTests(APITestCase):

#     def setUp(self):
#         self.user_data = {
#             'username': 'admin',
#             'email': 'admin@example.com',
#             'password': 'testpass123'
#         }
#         self.superuser = User.objects.create_superuser(**self.user_data)
#         self.client.login(username='admin', password='testpass123')

#         self.provider_data = {
#             'user': self.superuser,
#             'location': "Downtown"
#         }
#         self.provider = ServiceProvider.objects.create(**self.provider_data)

#     def test_create_service_provider(self):
#         # Ensure no ServiceProvider exists for the user
#         ServiceProvider.objects.filter(user=self.superuser).delete()
#         url = reverse('serviceprovider-list')
#         data = {'location': "New Location", 'user': self.superuser.id}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(ServiceProvider.objects.count(), 1)  # Only one should exist now

#     def test_update_service_provider(self):
#         url = reverse('serviceprovider-detail', args=[self.provider.id])
#         data = {'location': "Updated Location"}
#         response = self.client.patch(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.provider.refresh_from_db()
#         self.assertEqual(self.provider.location, "Updated Location")

#     def test_delete_service_provider(self):
#         url = reverse('serviceprovider-detail', args=[self.provider.id])
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(ServiceProvider.objects.filter(id=self.provider.id).exists())


# class ServiceTests(APITestCase):

#     def setUp(self):
#         # Create a superuser or a user with necessary permissions
#         self.user = User.objects.create_user(username='serviceprovider', password='password', is_service_provider=True)
#         self.client.login(username='serviceprovider', password='password')

#         self.provider = ServiceProvider.objects.create(user=self.user, location="Downtown")
        
#         self.service_data = {
#             'provider': self.provider.id,
#             'name': "Wedding Dance",
#             'description': "Special dance for weddings",
#             'price': "200.00",
#             'category': "Dance",
#         }

#         self.service = Service.objects.create(
#             provider=self.provider,
#             name=self.service_data['name'],
#             description=self.service_data['description'],
#             price=self.service_data['price'],
#             category=self.service_data['category']
#         )

#     def test_create_service(self):
#         url = reverse('service-list')
#         response = self.client.post(url, self.service_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_update_service(self):
#         """Test the update functionality of a service."""
#         # Assuming 'service' is already created in setUp
#         url = reverse('service-detail', args=[self.service.id])
#         update_data = {
#             'name': "Updated Wedding Dance",
#             'description': "An updated special dance for weddings",
#             'price': "300.00",
#             'category': "Dance"
#         }
#         response = self.client.patch(url, update_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.service.refresh_from_db()
#         self.assertEqual(self.service.name, "Updated Wedding Dance")

#     def test_delete_service(self):
#         url = reverse('service-detail', args=[self.service.id])
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Service.objects.filter(id=self.service.id).exists())

#     def test_create_service_with_invalid_price(self):
#         url = reverse('service-list')
#         data = {'name': "Updated Wedding Dance", 'description': "An updated special dance for weddings", 'price': "-100.00", 'category': "Dance", 'provider': self.provider.id}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('price', response.data)

#     def test_create_service_without_name(self):
#         url = reverse('service-list')
#         data = {'description': "An updated special dance for weddings", 'price': "300.00", 'category': "Dance", 'provider': self.provider.id}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('name', response.data)

#     def test_create_service_with_nonexistent_provider(self):
#         url = reverse('service-list')
#         data = {'name': "Updated Wedding Dance", 'description': "An updated special dance for weddings", 'price': "300.00", 'category': "Dance", 'provider': 9999}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('provider', response.data)

# class AuthorizationTests(APITestCase):
#     def setUp(self):
#         self.superuser = User.objects.create_superuser(username='adminsuper', email='adminsuper@example.com', password='testpass123')
#         self.client.login(username='adminsuper', password='testpass123')

#         self.normal_user = User.objects.create_user(username='normaluser', email='normaluser@example.com', password='userpass123')

#         self.provider = ServiceProvider.objects.create(user=self.superuser, location="Downtown")

#     def test_normal_user_cannot_create_service_provider(self):
#         self.client.logout()
#         self.client.login(username='normaluser', password='userpass123')
#         url = reverse('serviceprovider-list')
#         data = {'location': "New Location"}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_normal_user_cannot_delete_service_provider(self):
#         self.client.logout()
#         self.client.login(username='normaluser', password='userpass123')
#         url = reverse('serviceprovider-detail', args=[self.provider.id])
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# class ClientFunctionalityTests(APITestCase):
#     def setUp(self):
#         # Create a client user
#         self.client_user = User.objects.create_user(username='clientuser', password='password', is_service_provider=False)
#         self.client_instance = Client.objects.create(user=self.client_user)
#         self.client.login(username='clientuser', password='password')

#         # Setup a service provider and a service
#         self.provider_user = User.objects.create_user(username='provideruser', password='password', is_service_provider=True)
#         self.provider = ServiceProvider.objects.create(user=self.provider_user, location="Provider Location")
#         self.service = Service.objects.create(
#             provider=self.provider, 
#             name="Dance", 
#             description="Dance service", 
#             price=100.00, 
#             category="Entertainment"
#         )

#     def test_client_view_service(self):
#         url = reverse('service-list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_client_book_service(self):
#         future_date = now() + timedelta(days=10)
#         formatted_date = future_date.strftime('%Y-%m-%dT%H:%M:%SZ')
#         url = reverse('booking-list')
#         data = {
#             'service': self.service.id, 
#             'booking_date': formatted_date
#         }
#         response = self.client.post(url, data, format='json')
#         if response.status_code != status.HTTP_201_CREATED:
#             print(f'Failed to create booking: {response.data}')  # This will print the error details
#             print(f"Booking response status: {response.status_code}")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_client_restricted_from_creating_services(self):
#         url = reverse('service-list')
#         data = {'name': "Unauthorized Service", 'description': "Should not be allowed", 'price': 300.00, 'category': "Dance", 'provider': self.provider.id}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# class ServiceProviderPermissionTests(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='normaluser', password='password')
#         self.service_provider_user = User.objects.create_user(username='provideruser', password='password', is_service_provider=True)
#         self.superuser = User.objects.create_superuser(username='admin', email='admin@example.com', password='testpass123')

#     def test_create_service_provider_by_unauthorized_user(self):
#         self.client.login(username='normaluser', password='password')
#         url = reverse('serviceprovider-list')
#         response = self.client.post(url, {'location': 'Downtown'})
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_create_service_provider_by_authorized_user(self):
#         self.client.login(username='provideruser', password='password')
#         url = reverse('serviceprovider-list')
#         response = self.client.post(url, {'location': 'Downtown'})
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_create_service_provider_by_superuser(self):
#         self.client.login(username='admin', password='testpass123')
#         url = reverse('serviceprovider-list')
#         response = self.client.post(url, {'location': 'Downtown'})
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class RecommendationSystemTests(APITestCase):
    def setUp(self):
        # Set up data for testing the recommendation system
        self.client_user = User.objects.create_user(username='clientuser', email='client@example.com', password='testpass')
        self.client_instance = Client.objects.create(user=self.client_user)
        self.client.login(username='clientuser', password='testpass')
        # Creating multiple service providers
        self.service_provider_user = User.objects.create_user(username='provideruser', email='provider@example.com', password='testpass', is_service_provider=True)
        self.provider = ServiceProvider.objects.create(user=self.service_provider_user, location="Downtown", average_rating=4.5)
        # Adding services for the provider
        self.service = Service.objects.create(provider=self.provider, name="Dance Service", description="Professional dance service for events", price=300.00, category="Dance")

    def test_recommendation_accuracy(self):
        # Simulate the scenario where a client is looking for a high-rated dance service within budget
        url = reverse('service-search-recommendations')  # Ensure you have this endpoint configured
        response = self.client.get(url, {'category': 'Dance', 'max_price': 350, 'min_rating': 4})
        print("Recommendation Accuracy Test Response:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(service['provider']['average_rating'] >= 4 for service in response.data))

    def test_recommendation_efficiency(self):
        # Test the speed and efficiency of the recommendation system
        import time
        start_time = time.time()
        url = reverse('service-search-recommendations')
        self.client.get(url, {'category': 'Dance', 'max_price': 500, 'min_rating': 3})
        end_time = time.time()
        duration = end_time - start_time
        print("Recommendation Efficiency Test Duration:", duration)
        self.assertLess(duration, 2)  # Example criterion: the response must be returned in less than 2 seconds

### Service Search Tests
# These tests verify the functionality of searching and filtering services based on different parameters.

# class ServiceSearchTests(APITestCase):
#     def setUp(self):
#         # Basic setup for service search tests
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')
#         self.provider = ServiceProvider.objects.create(user=self.user, location="Central")
#         self.service = Service.objects.create(provider=self.provider, name="Party Planning", description="Plan the best parties with us", price=150.00, category="Event Planning")

#     def test_service_filtering(self):
#         # Testing filtering functionality
#         url = reverse('service-list')
#         response = self.client.get(url, {'category': 'Event Planning', 'max_price': 200})
#         print("Service Filtering Test Response:", response.data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTrue(all(service['price'] <= 200 for service in response.data))

#     def test_incomplete_criteria_matching(self):
#         # Test where expected no matches due to low max_price
#         url = reverse('service-list')
#         response = self.client.get(url, {'category': 'Event Planning', 'max_price': 100})
#         print("Incomplete Criteria Matching Test Response:", response.data)
#         # Check if response is empty or all services have prices greater than $100
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTrue(len(response.data) == 0 or all(service['price'] > 100 for service in response.data), "Response should not include any services priced under $100.")