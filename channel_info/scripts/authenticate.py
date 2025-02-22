from google.oauth2.credentials import Credentials  # Import Credentials class
import json  # Import json module to handle JSON file reading

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
from logger_factory import get_logger

logger = get_logger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def authenticate():
    creds = None
    try:
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            with open('token.json', 'r') as token:
                creds_data = json.load(token)
                creds = Credentials.from_authorized_user_info(creds_data)
                logger.info("Loaded credentials from token.json")

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logger.info("Refreshed expired credentials")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    './client_secret_579769589379-8f76ss5g4vnqadao4tohmje7ejfso66k.apps.googleusercontent.com.json', SCOPES)
                creds = flow.run_local_server(port=0)
                logger.info("Obtained new credentials via OAuth flow")
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                logger.info("Saved new credentials to token.json")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
    except Exception as e:
        logger.error(f"An error occurred during authentication: {e}")

    return creds


if __name__ == '__main__':
    credentials = authenticate()
    if credentials:
        logger.info("Authentication Successful!")
    else:
        logger.error("Authentication Failed!")
