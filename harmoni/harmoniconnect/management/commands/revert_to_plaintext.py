import json
from django.core.management.base import BaseCommand
from harmoniconnect.models import ServiceProvider
from json.decoder import JSONDecodeError

class Command(BaseCommand):
    help = 'Revert JSON fields to plain text'

    def handle(self, *args, **options):
        service_providers = ServiceProvider.objects.all()
        for provider in service_providers:
            try:
                # Revert offers
                if provider.offers and isinstance(provider.offers, str):
                    offers_list = json.loads(provider.offers)
                    if isinstance(offers_list, list) and len(offers_list) > 0:
                        provider.offers = offers_list[0]

                # Revert pricing
                if provider.pricing and isinstance(provider.pricing, str):
                    pricing_list = json.loads(provider.pricing)
                    if isinstance(pricing_list, list) and len(pricing_list) > 0:
                        provider.pricing = pricing_list[0]

                # Revert availability_description
                if provider.availability_description and isinstance(provider.availability_description, str):
                    availability_list = json.loads(provider.availability_description)
                    if isinstance(availability_list, list) and len(availability_list) > 0:
                        provider.availability_description = availability_list[0]

                provider.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully reverted provider: {provider.name}'))
            except JSONDecodeError:
                # If JSONDecodeError occurs, assume the data is already in plain text format
                self.stdout.write(self.style.WARNING(f'Provider {provider.name} already in plain text format. Skipping...'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing provider {provider.name}: {e}'))