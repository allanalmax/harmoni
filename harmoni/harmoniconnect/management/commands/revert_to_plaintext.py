import json
from django.core.management.base import BaseCommand
from harmoniconnect.models import ServiceProvider
from json.decoder import JSONDecodeError

class Command(BaseCommand):
    help = 'Revert JSON fields to plain text format and handle corrupted data'

    def handle(self, *args, **kwargs):
        service_providers = ServiceProvider.objects.all()
        for provider in service_providers:
            try:
                # Revert offers field
                if self.is_json(provider.offers):
                    offers_list = json.loads(provider.offers)
                    provider.offers = '\n'.join(offers_list)
                
                # Revert pricing field
                if self.is_json(provider.pricing):
                    pricing_list = json.loads(provider.pricing)
                    provider.pricing = '\n'.join(pricing_list)
                
                # Revert availability_description field
                if self.is_json(provider.availability_description):
                    availability_list = json.loads(provider.availability_description)
                    provider.availability_description = '\n'.join(availability_list)

                provider.save()
                self.stdout.write(self.style.SUCCESS(f'Reverted fields for {provider.name}'))

            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(f'Error decoding JSON for {provider.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully reverted all service providers'))

    def is_json(self, myjson):
        try:
            json.loads(myjson)
        except ValueError:
            return False
        return True