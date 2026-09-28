import os

from dotenv import load_dotenv


load_dotenv()


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured")


# ---------------------- Razorpay ---------------------- #

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

if not RAZORPAY_KEY_ID:
    raise RuntimeError("RAZORPAY_KEY_ID is not configured")

if not RAZORPAY_KEY_SECRET:
    raise RuntimeError("RAZORPAY_KEY_SECRET is not configured")




#------------------------------Email Integration------------------------#

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")

if not SMTP_HOST:
    raise RuntimeError("SMTP_HOST is not configured")

if not SMTP_USERNAME:
    raise RuntimeError("SMTP_USERNAME is not configured")

if not SMTP_PASSWORD:
    raise RuntimeError("SMTP_PASSWORD is not configured")

if not SMTP_FROM_EMAIL:
    raise RuntimeError("SMTP_FROM_EMAIL is not configured")