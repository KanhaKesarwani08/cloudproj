import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer # Can be repurposed for Bearer token
import os

# Initialize Firebase Admin SDK
# Ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set to the path of your service account key file.
# For Cloud Run, this can be managed by attaching a service account with appropriate permissions or by using Secret Manager.

# Check if Firebase app is already initialized to prevent re-initialization error
if not firebase_admin._apps:
    try:
        # If GOOGLE_APPLICATION_CREDENTIALS is set, it will be used automatically.
        # Otherwise, you might need to explicitly pass credential path for local dev if not using env var.
        # cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        # if cred_path:
        #     cred = credentials.Certificate(cred_path)
        #     firebase_admin.initialize_app(cred)
        # else:
        #     # For environments like Cloud Run where service account is implicit
        firebase_admin.initialize_app()
        print("Firebase Admin SDK initialized.")
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")
        # Depending on policy, you might want to raise an error or allow app to run with auth disabled

# This scheme can be used to extract the token from the Authorization header
# It expects a header like "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # tokenUrl is nominal here as Firebase handles token issuance

async def verify_firebase_token(token: str = Depends(oauth2_scheme)):
    if not firebase_admin._apps:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase Admin SDK not initialized. Cannot verify token."
        )
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except firebase_admin.auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Catch any other Firebase Admin SDK errors during verification
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not verify token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Dependency to get current user from Firebase token
async def get_current_user(decoded_token: dict = Depends(verify_firebase_token)):
    # You can extract user information from the decoded_token
    # For example, user_id (uid), email, etc.
    # You might want to create/fetch a corresponding user from your own database here if needed.
    # For now, just return the claims.
    return decoded_token 