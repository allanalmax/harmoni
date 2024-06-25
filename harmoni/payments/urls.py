from django.urls import path
from . import views

urlpatterns = [
    path('momo/', views.momo_payment, name='momo_payment'),
    path('momo/notify/', views.momo_notify, name='momo_notify'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_failure/', views.payment_failure, name='payment_failure'),
]
