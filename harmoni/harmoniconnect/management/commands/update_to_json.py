import json
from django.core.management.base import BaseCommand
from harmoniconnect.models import ServiceProvider

class Command(BaseCommand):
    help = 'Update plain text fields to JSON format'

    def handle(self, *args, **options):
        service_providers = ServiceProvider.objects.all()
        for provider in service_providers:
            try:
                # Update offers
                if provider.offers and not isinstance(provider.offers, list):
                    provider.offers = json.dumps(provider.offers.splitlines())
                # Update pricing
                if provider.pricing and not isinstance(provider.pricing, list):
                    provider.pricing = json.dumps(provider.pricing.splitlines())
                # Update availability_description
                if provider.availability_description and not isinstance(provider.availability_description, list):
                    provider.availability_description = json.dumps(provider.availability_description.splitlines())

                provider.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated provider: {provider.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating provider: {provider.name}, {e}'))

