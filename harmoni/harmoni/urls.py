from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from harmoniconnect import views
from harmoniconnect.views import ServiceViewSet, ServiceProviderViewSet, BookingViewSet, ReviewViewSet, SignUpView, ServiceSearchViewSet
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'serviceproviders', ServiceProviderViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'services/search', ServiceSearchViewSet, basename='service-search')

# # Print URLs for debugging
# for url_pattern in router.urls:
#     print(url_pattern)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
]

# Handling static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Optional: Add custom error handling views
# handler404 = 'your_app.views.custom_404_view'
# handler500 = 'your_app.views.custom_500_view'
