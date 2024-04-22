from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import ServiceProvider, Service, Client
from decimal import Decimal
from django.utils.timezone import now, timedelta

User = get_user_model()

class ServiceProviderTests(APITestCase):

    def setUp(self):
        self.user_data = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'testpass123'
        }
        self.superuser = User.objects.create_superuser(**self.user_data)
        self.client.login(username='admin', password='testpass123')

        self.provider_data = {
            'user': self.superuser,
            'location': "Downtown"
        }
        self.provider = ServiceProvider.objects.create(**self.provider_data)

    def test_create_service_provider(self):
        # Ensure no ServiceProvider exists for the user
        ServiceProvider.objects.filter(user=self.superuser).delete()
        url = reverse('serviceprovider-list')
        data = {'location': "New Location", 'user': self.superuser.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ServiceProvider.objects.count(), 1)  # Only one should exist now

    def test_update_service_provider(self):
        url = reverse('serviceprovider-detail', args=[self.provider.id])
        data = {'location': "Updated Location"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.location, "Updated Location")

    def test_delete_service_provider(self):
        url = reverse('serviceprovider-detail', args=[self.provider.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ServiceProvider.objects.filter(id=self.provider.id).exists())


class ServiceTests(APITestCase):

    def setUp(self):
        # Create a superuser or a user with necessary permissions
        self.user = User.objects.create_user(username='serviceprovider', password='password', is_service_provider=True)
        self.client.login(username='serviceprovider', password='password')

        self.provider = ServiceProvider.objects.create(user=self.user, location="Downtown")
        
        self.service_data = {
            'provider': self.provider.id,
            'name': "Wedding Dance",
            'description': "Special dance for weddings",
            'price': "200.00",
            'category': "Dance",
        }

        self.service = Service.objects.create(
            provider=self.provider,
            name=self.service_data['name'],
            description=self.service_data['description'],
            price=self.service_data['price'],
            category=self.service_data['category']
        )

    def test_create_service(self):
        url = reverse('service-list')
        response = self.client.post(url, self.service_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_service(self):
        """Test the update functionality of a service."""
        # Assuming 'service' is already created in setUp
        url = reverse('service-detail', args=[self.service.id])
        update_data = {
            'name': "Updated Wedding Dance",
            'description': "An updated special dance for weddings",
            'price': "300.00",
            'category': "Dance"
        }
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.service.refresh_from_db()
        self.assertEqual(self.service.name, "Updated Wedding Dance")

    def test_delete_service(self):
        url = reverse('service-detail', args=[self.service.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Service.objects.filter(id=self.service.id).exists())

    def test_create_service_with_invalid_price(self):
        url = reverse('service-list')
        data = {'name': "Updated Wedding Dance", 'description': "An updated special dance for weddings", 'price': "-100.00", 'category': "Dance", 'provider': self.provider.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)

    def test_create_service_without_name(self):
        url = reverse('service-list')
        data = {'description': "An updated special dance for weddings", 'price': "300.00", 'category': "Dance", 'provider': self.provider.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_service_with_nonexistent_provider(self):
        url = reverse('service-list')
        data = {'name': "Updated Wedding Dance", 'description': "An updated special dance for weddings", 'price': "300.00", 'category': "Dance", 'provider': 9999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('provider', response.data)

class AuthorizationTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='adminsuper', email='adminsuper@example.com', password='testpass123')
        self.client.login(username='adminsuper', password='testpass123')

        self.normal_user = User.objects.create_user(username='normaluser', email='normaluser@example.com', password='userpass123')

        self.provider = ServiceProvider.objects.create(user=self.superuser, location="Downtown")

    def test_normal_user_cannot_create_service_provider(self):
        self.client.logout()
        self.client.login(username='normaluser', password='userpass123')
        url = reverse('serviceprovider-list')
        data = {'location': "New Location"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_cannot_delete_service_provider(self):
        self.client.logout()
        self.client.login(username='normaluser', password='userpass123')
        url = reverse('serviceprovider-detail', args=[self.provider.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ClientFunctionalityTests(APITestCase):
    def setUp(self):
        # Create a client user
        self.client_user = User.objects.create_user(username='clientuser', password='password', is_service_provider=False)
        self.client_instance = Client.objects.create(user=self.client_user)
        self.client.login(username='clientuser', password='password')

        # Setup a service provider and a service
        self.provider_user = User.objects.create_user(username='provideruser', password='password', is_service_provider=True)
        self.provider = ServiceProvider.objects.create(user=self.provider_user, location="Provider Location")
        self.service = Service.objects.create(
            provider=self.provider, 
            name="Dance", 
            description="Dance service", 
            price=100.00, 
            category="Entertainment"
        )

    def test_client_view_service(self):
        url = reverse('service-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_book_service(self):
        future_date = now() + timedelta(days=10)
        formatted_date = future_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        url = reverse('booking-list')
        data = {
            'service': self.service.id, 
            'booking_date': formatted_date
        }
        response = self.client.post(url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(f'Failed to create booking: {response.data}')  # This will print the error details
            print(f"Booking response status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_client_restricted_from_creating_services(self):
        url = reverse('service-list')
        data = {'name': "Unauthorized Service", 'description': "Should not be allowed", 'price': 300.00, 'category': "Dance", 'provider': self.provider.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ServiceProviderPermissionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='normaluser', password='password')
        self.service_provider_user = User.objects.create_user(username='provideruser', password='password', is_service_provider=True)
        self.superuser = User.objects.create_superuser(username='admin', email='admin@example.com', password='testpass123')

    def test_create_service_provider_by_unauthorized_user(self):
        self.client.login(username='normaluser', password='password')
        url = reverse('serviceprovider-list')
        response = self.client.post(url, {'location': 'Downtown'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_service_provider_by_authorized_user(self):
        self.client.login(username='provideruser', password='password')
        url = reverse('serviceprovider-list')
        response = self.client.post(url, {'location': 'Downtown'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_service_provider_by_superuser(self):
        self.client.login(username='admin', password='testpass123')
        url = reverse('serviceprovider-list')
        response = self.client.post(url, {'location': 'Downtown'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)