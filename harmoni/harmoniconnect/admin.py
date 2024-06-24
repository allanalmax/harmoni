from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ServiceProvider, Client, Service, Booking, Review, Payment, EventDetails, Notification

class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'location')
    search_fields = ['user__username', 'location']

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'price', 'category')
    list_filter = ('category', 'provider')
    search_fields = ['name', 'provider__user__username']

class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'booking_date', 'status')
    list_filter = ('status', 'booking_date')
    search_fields = ['client__user__username', 'service__name']

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        ('User Info', {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email','is_service_provider', 'phone_number' )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    
#Changed User admin fields showcase. Solved the password hashed issue.
admin.site.register(CustomUser, CustomUserAdmin)

# admin.site.register(CustomUser)
admin.site.register(ServiceProvider, ServiceProviderAdmin)
admin.site.register(Client)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Review)
admin.site.register(Payment)
admin.site.register(EventDetails)
admin.site.register(Notification)
