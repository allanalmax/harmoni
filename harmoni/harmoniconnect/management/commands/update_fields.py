import json
from django.core.management.base import BaseCommand
from harmoniconnect.models import ServiceProvider

class Command(BaseCommand):
    help = 'Update offers, pricing, and availability fields to JSON format'

    def handle(self, *args, **kwargs):
        service_providers = ServiceProvider.objects.all()
        for provider in service_providers:
            # Update offers field
            if not self.is_json(provider.offers):
                offers_list = provider.offers.split('\n')
                offers_list = [offer.strip() for offer in offers_list if offer.strip()]
                provider.offers = json.dumps(offers_list)
            
            # Update pricing field
            if not self.is_json(provider.pricing):
                pricing_list = provider.pricing.split('\n')
                pricing_list = [price.strip() for price in pricing_list if price.strip()]
                provider.pricing = json.dumps(pricing_list)
            
            # Update availability_description field
            if not self.is_json(provider.availability_description):
                availability_list = provider.availability_description.split('\n')
                availability_list = [avail.strip() for avail in availability_list if avail.strip()]
                provider.availability_description = json.dumps(availability_list)

            provider.save()
            self.stdout.write(self.style.SUCCESS(f'Updated fields for {provider.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully updated all service providers'))

    def is_json(self, myjson):
        try:
            json.loads(myjson)
        except ValueError:
            return False
        return True
