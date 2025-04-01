import requests
import logging

logger = logging.getLogger(__name__)

class MSGraphClient:
    def __init__(self, config, access_token):
        self.config = config
        self.access_token = access_token

    async def get_all_users(self):
        """
        Get all users in the tenant using '/users' with app-only permissions.
        """
        try:
            endpoint = self.config.get("endpoint", "https://graph.microsoft.com/v1.0/users")
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting all users: {str(e)}"

    async def get_logged_in_user(self):
        """
        Fetch the currently logged in user's data using the '/me' endpoint.
        """
        try:
            endpoint = "https://graph.microsoft.com/v1.0/me"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error retrieving logged in user: {str(e)}")
            return f"Error getting logged in user: {str(e)}"
    
    async def find_user_by_name(self, name):
        """
        Search for users by displayName.
        """
        try:
            endpoint = f"{self.config.get('endpoint', 'https://graph.microsoft.com/v1.0/users')}?$filter=startswith(displayName,'{name}')"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error searching users: {str(e)}"

    async def get_user_profile(self, user_identifier):
        """
        Fetch the user's profile '/users/{id}'.
        """
        try:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{user_identifier}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting profile: {str(e)}"

    async def get_manager_info(self, user_identifier):
        """
        Fetch the user's manager via '/users/{id}/manager'.
        """
        try:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{user_identifier}/manager"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting manager info: {str(e)}"

    async def get_direct_reports(self, user_identifier):
        """
        Fetch the user's direct reports '/users/{id}/directReports'.
        """
        try:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{user_identifier}/directReports"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting direct reports: {str(e)}"

    async def get_devices(self, user_identifier):
        """
        Fetch the user's devices '/users/{id}/managedDevices'.
        """
        try:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{user_identifier}/managedDevices"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting devices: {str(e)}"

    async def get_colleagues(self, user_identifier):
        """
        Fetch 'people' data for the user (may need delegated perms).
        """
        try:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{user_identifier}/people"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting colleagues: {str(e)}"

    async def get_documents(self, user_identifier):
        """
        Fetch the user's recent documents '/users/{id}/drive/recent'.
        """
        try:
            endpoint = f"https://graph.microsoft.com/v1.0/users/{user_identifier}/drive/recent"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error getting documents: {str(e)}"