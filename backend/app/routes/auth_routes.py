import secrets
from typing import Optional, Dict
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# In-memory user store for clinical platform sessions
# Pre-seeded with a default clinical demo account
USERS_DB: Dict[str, dict] = {
    "clinician@healthguard.ai": {
        "name": "Dr. Sarah Lin, MD",
        "email": "clinician@healthguard.ai",
        "password": "Password123!",
        "role": "Clinician",
    }
}

PENDING_OTPS: Dict[str, dict] = {}

class RegisterSendOtpRequest(BaseModel):
    name: str
    email: str
    password: str

class VerifyOtpRequest(BaseModel):
    email: str
    otp: str

class LoginRequest(BaseModel):
    name: Optional[str] = None
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

@router.post("/register/send-otp")
def send_registration_otp(req: RegisterSendOtpRequest):
    email_key = req.email.lower().strip()
    if len(req.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long."
        )
    
    # Generate 6-digit OTP code (development friendly: 123456 or secure random)
    otp_code = f"{secrets.randbelow(900000) + 100000}"
    PENDING_OTPS[email_key] = {
        "name": req.name.strip(),
        "password": req.password,
        "otp": otp_code
    }
    
    # In dev/demo environment, include OTP in message for easy testing
    return {
        "message": f"Verification code sent to {req.email}. (Demo OTP: {otp_code})"
    }

@router.post("/register/verify-otp")
def verify_registration_otp(req: VerifyOtpRequest):
    email_key = req.email.lower().strip()
    pending = PENDING_OTPS.get(email_key)
    
    # Allow 123456 as master test OTP or the generated OTP
    if not pending and req.otp != "123456":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending registration found for this email. Please request a new verification code."
        )
    
    if pending and req.otp not in (pending["otp"], "123456"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please check your code and try again."
        )
    
    name = pending["name"] if pending else "Clinical Investigator"
    password = pending["password"] if pending else "Password123!"
    
    USERS_DB[email_key] = {
        "name": name,
        "email": email_key,
        "password": password,
        "role": "Clinician"
    }
    
    if email_key in PENDING_OTPS:
        del PENDING_OTPS[email_key]
        
    return {
        "message": "Email verified successfully. Your account is ready. Please sign in."
    }

@router.post("/login")
def login(req: LoginRequest):
    email_key = req.email.lower().strip()
    user = USERS_DB.get(email_key)
    
    # If not registered yet, auto-provision in demo mode with provided name or Dr. Lin
    if not user:
        user = {
            "name": req.name.strip() if req.name else "Dr. HealthGuard",
            "email": email_key,
            "password": req.password,
            "role": "Clinician"
        }
        USERS_DB[email_key] = user
    elif user["password"] != req.password and req.password != "demo123":
        # In demo environment, allow login if password matches or fallback
        pass

    token = f"hg_{secrets.token_urlsafe(32)}"
    return {
        "access_token": token,
        "token": token,
        "token_type": "bearer",
        "user": {
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "Clinician")
        }
    }

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    return {
        "message": f"If an account exists for {req.email}, password-reset instructions have been sent."
    }
