import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

client_secret_file = 'credentials.json'

sheets_api_name = 'sheets'
sheets_api_version = 'v4'
# Scope tells what authorization the service can perform.
sheets_scope = 'https://www.googleapis.com/auth/spreadsheets'

drive_api_name = 'drive'
drive_api_version = 'v3'
drive_scope = 'https://www.googleapis.com/auth/drive.file'

def create_service(client_secret_file, api_name, api_version, *scopes):
    """This service provides access to Google's APIs given authorization.
    Args:
        client_secret_file (str): The path to the client secret file
        api_name (str): The name of the specific Google API to use
        api_version (str): The version of the API to use
        scopes (str): The scopes to request access to
    Returns:
        service: The service object that can be used to interact with the specific API
    """
    client_secret_file = client_secret_file
    api_service_name = api_name
    api_version = api_version
    scopes = scopes

    cred = None

    # The pickle file saves access to Google's APIs so you don't need to request access every time
    # you use a Google product
    pickle_file = f'{api_service_name}_{api_version}_token.pickle'

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_service_name, api_version, credentials=cred)
        print(api_service_name, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None
    
sheets_service = create_service(client_secret_file, sheets_api_name, sheets_api_version, sheets_scope)
drive_service = create_service(client_secret_file, drive_api_name, drive_api_version, drive_scope)