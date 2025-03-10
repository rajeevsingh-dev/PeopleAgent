import msal
import logging

logger = logging.getLogger(__name__)

def get_access_token(config):
    """
    Acquire access token using MSAL (client credentials).
    """
    app = msal.ConfidentialClientApplication(
        client_id=config["client_id"],
        authority=config["authority"],
        client_credential=config["secret"]
    )

    result = app.acquire_token_silent(config["scope"], account=None)
    if not result:
        logger.info("No token in cache. Getting new token...")
        result = app.acquire_token_for_client(scopes=config["scope"])

    if "access_token" in result:
        return result["access_token"]
    else:
        logger.error(f"Error getting token: {result.get('error')}")
        logger.error(f"Error description: {result.get('error_description')}")
        return None