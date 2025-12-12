"""
JWT Authentication Utilities
Handles JWT token decoding and user extraction
"""

import os
from typing import Optional
from fastapi import HTTPException, Request, Cookie
import jwt
from dotenv import load_dotenv

load_dotenv()

ACCESS_JWT_SECRET = os.getenv("ACCESS_JWT_SECRET")
print(f"🔐 JWT Secret loaded: {'Yes' if ACCESS_JWT_SECRET else 'No'} (length: {len(ACCESS_JWT_SECRET) if ACCESS_JWT_SECRET else 0})")


def decode_access_token(token: str) -> dict:
    """
    Decode and verify JWT access token
    
    Args:
        token: The JWT token string
    
    Returns:
        The decoded payload containing user info
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode without verification first to see the payload
        unverified = jwt.decode(token, options={"verify_signature": False})
        print(f"🔍 Token payload (unverified): {unverified}")
        
        # Now verify properly
        payload = jwt.decode(token, ACCESS_JWT_SECRET, algorithms=["HS256"])
        print(f"✅ Token verified successfully: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        print("❌ Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid token: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from JWT token
    
    Args:
        token: The JWT token string
    
    Returns:
        The user ID or None if not found
    """
    try:
        payload = decode_access_token(token)
        # The user ID might be in 'id', 'userId', 'user_id', or 'sub' field
        return payload.get("id") or payload.get("userId") or payload.get("user_id") or payload.get("sub")
    except HTTPException:
        return None


def get_token_from_request(request: Request, access_token: Optional[str] = Cookie(None)) -> Optional[str]:
    """
    Extract token from request (cookie or Authorization header)
    
    Args:
        request: The FastAPI request object
        access_token: Token from cookie
    
    Returns:
        The token string or None
    """
    # First check Authorization header
    auth_header = request.headers.get("Authorization")
    print(f"🔍 Authorization header: {auth_header[:50] if auth_header else 'None'}...")
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Remove "Bearer " prefix
        print(f"🎫 Token from header: {token[:30]}...")
        return token
    
    # Then check cookie
    if access_token:
        print(f"🍪 Token from cookie param: {access_token[:30]}...")
        return access_token
    
    # Check for access_token in cookies dict
    token = request.cookies.get("access_token")
    if token:
        print(f"🍪 Token from cookies dict: {token[:30]}...")
        return token
    
    print("⚠️ No token found in request")
    return None


async def get_current_user_id(request: Request, access_token: Optional[str] = Cookie(None)) -> Optional[str]:
    """
    Get current user ID from request
    
    Args:
        request: The FastAPI request object
        access_token: Token from cookie
    
    Returns:
        The user ID or None if not authenticated
    """
    token = get_token_from_request(request, access_token)
    if not token:
        return None
    
    return get_user_id_from_token(token)
