from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from harmoniconnect import views
from harmoniconnect.views import ServiceViewSet, ServiceProviderViewSet, BookingViewSet, ReviewViewSet, SignUpView, ServiceSearchViewSet
from harmoniconnect.views import CustomLoginView
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import LoginView

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'serviceproviders', ServiceProviderViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'services/search', ServiceSearchViewSet, basename='service-search')

# # Print URLs for debugginga
# for url_pattern in router.urls:
#     print(url_pattern)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('register/customer/', views.customer_register, name='customer_register'),
    path('register/provider/', views.provider_register, name='provider_register'),
    path('search/', views.search, name='search'),
    path('service-providers/<int:service_provider_id>/', views.service_detail, name='service_detail'),
    path('service-provider-dashboard/', views.provider_dashboard, name='service_provider_dashboard'),
    path('support/', views.support, name='support'),
    path('client_dashboard/', views.client_dashboard, name='client_dashboard'),
    # path('test_search/', views.test_search, name='test_search'),
]

# Handling static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Optional: Add custom error handling views
# handler404 = 'your_app.views.custom_404_view'
# handler500 = 'your_app.views.custom_500_view'
