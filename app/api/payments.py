from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/razorpay-config")
async def get_razorpay_config():
    """Returns the Razorpay payment button ID for frontend embedding."""
    return {
        "payment_button_id": settings.RAZORPAY_PAYMENT_BUTTON_ID,
        "script_url": "https://checkout.razorpay.com/v1/payment-button.js",
    }
