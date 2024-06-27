from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Service, ServiceProvider, Booking, Review
from django.utils import timezone

class ServiceSerializer(serializers.ModelSerializer):
    provider = serializers.PrimaryKeyRelatedField(read_only=True)  # Use PrimaryKeyRelatedField

    class Meta:
        model = Service
        fields = '__all__'

    def validate_price(self, value):
        """
        Check that the price is a positive number.
        """
        if value <= 0:
            raise serializers.ValidationError("The price must be a positive number.")
        return value

class ServiceProviderSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    class Meta:
        model = ServiceProvider
        fields = ['id', 'name', 'average_rating', 'services']

class BookingSerializer(serializers.ModelSerializer):
    service_details = serializers.SerializerMethodField()
    provider_details = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'
        extra_kwargs = {'client': {'required': False}}
        read_only_fields = ['status']

    def get_service_details(self, obj):
        if obj.service:
            serializer = ServiceSerializer(obj.service)
            return serializer.data
        return None

    def get_provider_details(self, obj):
        if obj.service and obj.service.provider:
            serializer = ServiceProviderSerializer(obj.service.provider)
            return serializer.data
        return None
    
    def validate_client(self, value):
        user = self.context['request'].user
        if not user.is_staff and value != user.client:
            raise serializers.ValidationError("You do not have permission to create a booking for this client.")
        return value

    def validate(self, data):
        if 'booking_date' in data and data['booking_date'] < timezone.now():
            raise ValidationError("Booking cannot be made for a past date.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if 'client' not in validated_data:
            validated_data['client'] = self.context['request'].user.client
        return super().create(validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['booking', 'rating', 'comment']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['booking', 'reviewer'],
                message="One review per booking per reviewer."
            )
        ]
