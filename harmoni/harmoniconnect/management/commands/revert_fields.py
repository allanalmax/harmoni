import json
from django.core.management.base import BaseCommand
from harmoniconnect.models import ServiceProvider

class Command(BaseCommand):
    help = 'Revert offers, pricing, and availability fields from JSON format to plain text'

    def handle(self, *args, **kwargs):
        service_providers = ServiceProvider.objects.all()
        for provider in service_providers:
            try:
                # Revert offers field
                offers_list = json.loads(provider.offers)
                provider.offers = '\n'.join(offers_list)
            except json.JSONDecodeError:
                pass  # Already plain text

            try:
                # Revert pricing field
                pricing_list = json.loads(provider.pricing)
                provider.pricing = '\n'.join(pricing_list)
            except json.JSONDecodeError:
                pass  # Already plain text

            try:
                # Revert availability_description field
                availability_list = json.loads(provider.availability_description)
                provider.availability_description = '\n'.join(availability_list)
            except json.JSONDecodeError:
                pass  # Already plain text

            provider.save()
            self.stdout.write(self.style.SUCCESS(f'Reverted fields for {provider.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully reverted all service providers'))
