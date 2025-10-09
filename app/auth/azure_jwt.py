# app/auth/azure_jwt.py
import os
import time
import requests
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from cachetools import TTLCache, cached

TENANT_ID = os.getenv("AZURE_TENANT_ID", "<TENANT_ID>")
API_AUDIENCE = os.getenv("AZURE_API_AUDIENCE", "api://<BACKEND_CLIENT_ID>")

# discovery URL to get jwks / issuer
OPENID_CONFIG = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration"

# cache JWKS for 24 hours
jwks_cache = TTLCache(maxsize=1, ttl=24 * 60 * 60)


@cached(jwks_cache)
def get_openid_config():
    resp = requests.get(OPENID_CONFIG, timeout=10)
    resp.raise_for_status()
    return resp.json()


@cached(jwks_cache)
def get_jwks():
    config = get_openid_config()
    jwks_uri = config["jwks_uri"]
    resp = requests.get(jwks_uri, timeout=10)
    resp.raise_for_status()
    return resp.json()


def verify_access_token(token: str, audience: str = API_AUDIENCE) -> dict:
    """
    Verify the incoming Azure AD access token.
    Returns decoded claims on success, raises HTTPException on failure.
    """
    config = get_openid_config()
    issuer = config["issuer"]
    jwks = get_jwks()

    # Use jose to verify signature and claims
    try:
        # decode header to find kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        # Find key in jwks
        key = None
        for k in jwks["keys"]:
            if k["kid"] == kid:
                key = k
                break
        if key is None:
            raise JWTError("Public key not found in JWKS")

        # verify
        decoded = jwt.decode(
            token,
            key,
            algorithms=key.get("alg", "RS256"),
            audience=audience,
            issuer=issuer,
        )
        # Optional: additional checks (roles, scope)
        return decoded

    except ExpiredSignatureError as e:
        raise e
    except JWTError as e:
        raise e
