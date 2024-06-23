from django.urls import path, include

from harmoniconnect import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # Custom login view
    # path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/login/', views.login, name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('register/customer/', views.customer_register, name='customer_register'),
    path('register/provider/', views.provider_register, name='provider_register'),
    path('search/', views.search, name='search'),
    path('service-providers/<int:service_provider_id>/', views.service_detail, name='service_detail'),
    path('service-provider-dashboard/<int:service_provider_id>/', views.provider_dashboard, name='provider_dashboard'),
    path('support/', views.support, name='support'),
    path('client_dashboard/', views.client_dashboard, name='client_dashboard'),
    path('booking_success/', views.booking_success, name='booking_success'),
    path('reviews/', views.reviews, name='reviews'),
    path('book_service/', views.book_service, name='book_service'),

    # path('test_search/', views.test_search, name='test_search'),
]