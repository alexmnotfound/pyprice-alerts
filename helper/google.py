import os
import pickle
import logging
from typing import List, Any
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import discovery
from tenacity import retry, stop_after_attempt, wait_fixed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SheetsHelper:
    """
    Helper class for working with the Google Sheets API.
    """

    def __init__(
            self,
            path: str = os.getenv('CREDENTIALS_PATH', './credentials/'),
            credentials: str = os.getenv('CREDENTIALS_FILE', 'creds.json'),
            token: str = os.getenv('TOKEN_FILE', 'token.pickle'),
            scopes: List[str] = None):

        """
        Initializes the SheetsHelper object.

        :param path: str - The path to the credentials and token files (can be set via environment variables).
        :param credentials: str - The name of the credentials file (can be set via environment variables).
        :param token: str - The name of the token file (can be set via environment variables).
        :param scopes: list - The API scopes to authorize. Defaults to spreadsheets scope if None.
        """

        if scopes is None:
            scopes = ['https://www.googleapis.com/auth/spreadsheets']

        self.path = path
        self.credentials = os.path.join(path, credentials)
        self.token = os.path.join(path, token)
        self.scopes = scopes
        self.service = self.create_service()

    def create_service(self) -> discovery.Resource:
        """
        Check for creds file and create Google Sheets service.

        :return: Google Sheets service object.
        """
        creds = None

        if os.path.exists(self.token):
            with open(self.token, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials, self.scopes)
                creds = flow.run_local_server(port=0)

            with open(self.token, 'wb') as token:
                pickle.dump(creds, token)

        service = discovery.build('sheets', 'v4', credentials=creds, cache_discovery=False)
        return service

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_sheet_data(self, spreadsheet_id: str, sheet_range: str) -> List[List[Any]]:
        """
        Gets data from a specified range in a Google Sheet.

        :param spreadsheet_id: str - The ID of the Google Sheet.
        :param sheet_range: str - The range of cells to get data from.
        :return: list - Values from the specified range.
        :raises: Exception if any error occurs during the API request.
        """

        try:
            logger.info("Reading data from Google Sheets...\n")
            result = self.service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute()
            values = result.get('values', [])

            if not values:
                logger.warning('No data found.\n')
            return values

        except Exception as e:
            logger.error(f"An error occurred: {e}\n")
            raise  # Re-throwing the exception to be handled by the calling function.

    def append_values(self, spreadsheet_id: str, sheet_range: str, value_input_option: str, values: List[List[Any]]) -> Any:
        """
        Appends values to a new row on a specific sheet in a Google Sheet.

        :param spreadsheet_id: str - The ID of the Google Sheet.
        :param sheet_range: str - The range of cells to insert values into.
        :param value_input_option: str - How input data should be interpreted.
        :param values: list - The values to insert into the sheet.
        :return: Result of the append operation (dict) or Exception if an error occurred.
        """
        try:
            body = {'values': values}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id, range=sheet_range,
                valueInputOption=value_input_option, body=body).execute()
            logger.info(f"{(result.get('updates').get('updatedCells'))} cells appended.\n")
            return result

        except Exception as error:
            logger.error(f"An error occurred: {error}\n")
            raise  # Re-throwing the exception to be handled by the calling function.
