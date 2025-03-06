import sys 
import json
import os
import logging
import requests
import msal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from parameters.json in the same directory"""
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'parameters.json')
        
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)

def get_access_token(config):
    """Acquire access token using MSAL"""
    app = msal.ConfidentialClientApplication(
        client_id=config["client_id"],
        authority=config["authority"],
        client_credential=config["secret"]
    )

    # Try to get token from cache first
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

def get_users(access_token, endpoint):
    """Get users from Microsoft Graph"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Microsoft Graph: {str(e)}")
        return None

def main():
    # Load configuration
    config = load_config()

    # Get access token
    access_token = get_access_token(config)
    if not access_token:
        logger.error("Failed to acquire access token")
        return

    # Get user details
    users_data = get_users(access_token, config["endpoint"])
    if users_data:
        print("\nUser Details:")
        print(json.dumps(users_data, indent=2))
    else:
        logger.error("Failed to get user details")

if __name__ == "__main__":
    main()