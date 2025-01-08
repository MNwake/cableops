import stripe
import os
from dotenv import load_dotenv

load_dotenv()

class StripeManager:
    """A class to manage all Stripe-related interactions."""

    def __init__(self):
        self.secret_key = os.getenv("STRIPE_TEST_KEY")
        if not self.secret_key:
            raise ValueError("STRIPE_SECRET_KEY is not set in the environment variables.")
        stripe.api_key = self.secret_key

    def create_checkout_session(self, product_name: str, unit_amount: int, quantity: int, success_url: str,
                                cancel_url: str):
        """
        Create a Stripe Checkout session.

        Args:
            product_name (str): Name of the product being purchased.
            unit_amount (int): Price per unit in cents (e.g., 1000 = $10.00).
            quantity (int): Number of units.
            success_url (str): URL to redirect upon successful payment.
            cancel_url (str): URL to redirect upon cancellation.

        Returns:
            dict: Checkout session URL.
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": product_name},
                        "unit_amount": unit_amount,
                    },
                    "quantity": quantity,
                }],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return {"url": session.url}
        except Exception as e:
            print(f"Error creating Stripe session: {e}")
            raise e

    def retrieve_session(self, session_id: str):
        """
        Retrieve a Stripe Checkout session by its ID.

        Args:
            session_id (str): The ID of the session to retrieve.

        Returns:
            stripe.checkout.Session: The session object.
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except Exception as e:
            print(f"Error retrieving Stripe session: {e}")
            raise e

    def create_payment_intent(self, amount: int, currency: str = "usd"):
        """
        Create a Stripe Payment Intent.

        Args:
            amount (int): Amount in cents (e.g., 2000 = $20.00).
            currency (str): Currency code (default is USD).

        Returns:
            stripe.PaymentIntent: The Payment Intent object.
        """
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,  # Amount in cents
                currency=currency,
                payment_method_types=["card"],
            )
            print("Payment Intent Created:")
            return payment_intent
        except stripe.error.StripeError as e:
            print("Stripe Error:", e)
            raise e
        except Exception as e:
            print("Error:", e)
            raise e

    def test_payment_intent(self, amount: int = 2000):
        """
        Test the creation of a payment intent.

        Args:
            amount (int): Amount in cents for the test (default is $20.00).
        """
        try:
            payment_intent = self.create_payment_intent(amount=amount)
            print(f"Test Payment Intent Created: {payment_intent.id}")
        except Exception as e:
            print(f"Error during test payment intent creation: {e}")


if __name__ == "__main__":
    sm = StripeManager()
    sm.test_payment_intent()
