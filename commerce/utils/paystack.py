import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Paystack:
    PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
    BASE_URL = "https://api.paystack.co"

    @staticmethod
    def initialize_payment(email, amount):
        """Initialize payment with Paystack"""
        headers = {
            "Authorization": f"Bearer {Paystack.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "email": email,
            "amount": int(amount * 100),  # Convert amount to kobo
            "callback_url": settings.PAYSTACK_WALLET_CALLBACK_URL,
        }
        url = f"{Paystack.BASE_URL}/transaction/initialize"

        try:
            response = requests.post(url, json=data, headers=headers)  #start a payment for this user
            response.raise_for_status() #If Paystack returns error → stop execution
            return response.json()  #convert into python dictionary
        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack initialization failed: {e}")
            return {"status": False, "message": "Payment initialization failed."}


    @staticmethod
    def verify_payment(reference):
        """Verify payment status with Paystack"""
        headers = {
            "Authorization": f"Bearer {Paystack.PAYSTACK_SECRET_KEY}",
        }
        url = f"{Paystack.BASE_URL}/transaction/verify/{reference}"

        try:
            response = requests.get(url, headers=headers) #send get request and ask paystack did the user actually pay
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack verification failed: {e}")
            return {"status": False, "message": "Payment verification failed."}
