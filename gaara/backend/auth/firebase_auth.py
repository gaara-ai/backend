import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict
import logging
import os
import json

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


def initialize_firebase(service_account_path: str = None):
    """
    Initialize Firebase Admin SDK.
    Supports:
    - Local development (JSON file)
    - Production (FIREBASE_CONFIG env variable)
    """

    if firebase_admin._apps:
        logger.info("Firebase already initialized")
        return

    try:
        firebase_config_env = os.getenv("FIREBASE_CONFIG")

        if firebase_config_env:
            # 🔥 Production (Render)
            logger.info("Initializing Firebase from environment variable")
            cred = credentials.Certificate(json.loads(firebase_config_env))

        elif service_account_path:
            # 💻 Local development
            logger.info("Initializing Firebase from service account file")
            cred = credentials.Certificate(service_account_path)

        else:
            raise ValueError("Firebase credentials not provided")

        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict:
    """
    Verify Firebase ID token and return decoded token.
    """

    token = credentials.credentials

    try:
        decoded_token = auth.verify_id_token(token)

        logger.info(f"Token verified for user: {decoded_token.get('uid')}")

        return {
            "uid": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "email_verified": decoded_token.get("email_verified", False),
            "name": decoded_token.get("name"),
        }

    except auth.InvalidIdTokenError:
        logger.warning("Invalid Firebase token")
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    except auth.ExpiredIdTokenError:
        logger.warning("Expired Firebase token")
        raise HTTPException(status_code=401, detail="Authentication token has expired")

    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_current_user(token_data: Dict = Depends(verify_firebase_token)) -> Dict:
    """
    Get current authenticated user information.
    """
    return token_data
