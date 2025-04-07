import os
import sys
import logging
from dotenv import load_dotenv
from datetime import datetime
import json

logger = logging.getLogger(__name__)
load_dotenv()

class AppConfig:
    """
    Configuration class to handle application settings.
    """
    def __init__(self, config_path=None):
        self.config_data = {}
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'config', 'app_config.json')
        self.load_config()
    
    def load_config(self):
        """Load configuration from the JSON file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config_data = json.load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.warning(f"Config file not found at {self.config_path}, using default settings")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            
    def get(self, key, default=None):
        """Get a configuration value by key"""
        return self.config_data.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value"""
        self.config_data[key] = value
        
    def save_config(self):
        """Save the configuration back to the file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config_data, f, indent=4)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False


def load_config():
    """
    Load all configuration from environment variables.
    """
    try:
        scope_value = os.environ["SCOPE"].strip()
        if scope_value.startswith('[') and scope_value.endswith(']'):
            scope_value = scope_value[1:-1].strip('"\'')
        
        config = {
            # Microsoft Graph API
            "client_id": os.environ["CLIENT_ID"],
            "authority": os.environ["AUTHORITY"],
            "secret": os.environ["SECRET"],
            "scope": [scope_value],
            "endpoint": os.environ.get("ENDPOINT", "https://graph.microsoft.com/v1.0/users"),

            # Azure OpenAI
            "AOAI_ENDPOINT": os.environ["AOAI_ENDPOINT"],
            "AOAI_KEY": os.environ["AOAI_KEY"],
            "AOAI_DEPLOYMENT": os.environ["AOAI_DEPLOYMENT"],
            "AOAI_API_VERSION": os.environ.get("AOAI_API_VERSION", "2024-02-15-preview"),

            # Logging
            "logging": {
                "enabled": os.environ.get("LOGGING_ENABLED", "false").lower() == "true",
                "level": os.environ.get("LOGGING_LEVEL", "INFO"),
                "format": os.environ.get("LOGGING_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
                "log_file": os.environ.get("LOGGING_FILE", "people_agent_{timestamp}.log")
            }
        }
        return config
    except KeyError as e:
        logger.error(f"Missing required environment variable: {e}")
        sys.exit(1)