from fastapi import APIRouter, HTTPException
from Controller.stripe_manager import StripeManager

router = APIRouter()
stripe_manager = StripeManager()

@router.post("/create-checkout-session")
async def create_checkout_session():
    """
    API endpoint to create a Stripe Checkout session.

    Returns:
        dict: URL of the created session.
    """
    try:
        session_url = stripe_manager.create_checkout_session(
            product_name="Cable Token",
            unit_amount=1000,  # $10.00 in cents
            quantity=1,
            success_url="https://yourwebsite.com/success",
            cancel_url="https://yourwebsite.com/cancel",
        )
        return session_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/retrieve-session/{session_id}")
async def retrieve_session(session_id: str):
    """
    API endpoint to retrieve a Stripe Checkout session.

    Args:
        session_id (str): The ID of the session.

    Returns:
        stripe.checkout.Session: The session object.
    """
    try:
        session = stripe_manager.retrieve_session(session_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
