import json
from django.core.management.base import BaseCommand
from harmoniconnect.models import ServiceProvider

class Command(BaseCommand):
    help = 'Revert JSON fields to plain text'

    def handle(self, *args, **options):
        service_providers = ServiceProvider.objects.all()
        for provider in service_providers:
            try:
                # Revert offers
                if provider.offers and not isinstance(provider.offers, str):
                    provider.offers = json.dumps(provider.offers)

                # Revert pricing
                if provider.pricing and not isinstance(provider.pricing, str):
                    provider.pricing = json.dumps(provider.pricing)

                # Revert availability_description
                if provider.availability_description and not isinstance(provider.availability_description, str):
                    provider.availability_description = json.dumps(provider.availability_description)

                provider.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully reverted provider: {provider.name}'))
            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(f'Error decoding JSON for provider: {provider.name}'))