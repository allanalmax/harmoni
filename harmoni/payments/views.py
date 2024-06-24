# payments/views.py
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import MoMoPaymentForm
import requests
import uuid

def momo_payment(request):
    if request.method == "POST":
        form = MoMoPaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            phone_number = form.cleaned_data['phone_number']
            currency = "EUR"
            external_id = str(uuid.uuid4())
            payer = {"partyIdType": "MSISDN", "partyId": phone_number}
            payee_note = "Payment for event booking"
            payer_message = "Thank you for booking with us"
            callback_url = "http://f736-41-202-230-115.ngrok-free.app/payments/momo/notify/"


            url = f"https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay"

            headers = {
                "Authorization": f"Bearer {settings.MTN_MOMO_API_KEY}",
                "X-Target-Environment": settings.MTN_MOMO_ENVIRONMENT,
                "Ocp-Apim-Subscription-Key": settings.MTN_MOMO_SUBSCRIPTION_KEY,
                "Content-Type": "application/json",
            }

            data = {
                "amount": str(amount),
                "currency": currency,
                "externalId": external_id,
                "payer": payer,
                "payerMessage": payer_message,
                "payeeNote": payee_note,
                "callbackUrl": callback_url,
            }

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 202:
                return redirect('payment_success')
            else:
                return redirect('payment_failure')
    else:
        form = MoMoPaymentForm()

    return render(request, "momo_payment.html", {'form': form})

def payment_success(request):
    return render(request, "payment_success.html")

def payment_failure(request):
    return render(request, "payment_failure.html")

def momo_notify(request):
    # Handle the notification callback from MTN MoMo API
    return render(request, "payment_notification.html")
