"""
Authentication module for Google Calendar API
"""

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .config import SCOPES, CREDENTIALS_FILE, TOKEN_FILE


def get_calendar_service():
    """
    Authenticate and return the Google Calendar service.
    
    Returns:
        Google Calendar service instance
        
    Raises:
        FileNotFoundError: If credentials.json is not found
    """
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"'{CREDENTIALS_FILE}' not found. Please download it from Google Cloud Console."
        )
    
    creds = None
    
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)
