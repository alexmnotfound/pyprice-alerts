import os
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import discovery


class SheetsHelper:
    """
    Helper class for working with the Google Sheets API.
    """

    def __init__(
            self,
            path: str = './credentials/',
            credentials: str = 'creds.json',
            token: str = 'token.pickle',
            scopes: list = ['https://www.googleapis.com/auth/spreadsheets']):

        """
        Initializes the SheetsHelper object.

        :param path: str - The path to the credentials and token files.
        :param credentials: str - The name of the credentials file.
        :param token: str - The name of the token file.
        :param scopes: list - The API scopes to authorize.
        """

        self.path = path
        self.credentials = path + credentials
        self.token = path + token
        self.scopes = scopes
        self.service = self.create_service()

    def create_service(self):
        """
        Check for creds file and create Google Sheets service.

        :return: Google Sheets service object.
        """

        creds = None
        if os.path.exists(self.token):
            with open(self.token, 'rb') as token:
                creds = pickle.load(token)

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

    def get_sheet_data(self, spreadsheet_id, sheet_range):
        """
        Gets data from a specified range in a Google Sheet.

        :param spreadsheet_id: str - The ID of the Google Sheet.
        :param sheet_range: str - The range of cells to get data from.
        :return: list - Values from the specified range.
        """

        print("Reading data from Google Sheets...")
        result = self.service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute()
        result = result['values']
        return result

    def append_values(self, spreadsheet_id, sheet_range, value_input_option, values):
        """
        Appends values to a new row on a specific sheet in a Google Sheet.

        :param spreadsheet_id: str - The ID of the Google Sheet.
        :param sheet_range: str - The range of cells to insert values into.
        :param value_input_option: str - How input data should be interpreted.
        :param values: list - The values to insert into the sheet.
            Example:
                [
                    ['F', 'B'],
                    ['C', 'D']
                ]

        For more information, see https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append.
        """
        try:
            body = {'values': values}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id, range=sheet_range,
                valueInputOption=value_input_option, body=body).execute()
            print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
            return result

        except Exception as error:
            print(f"An error occurred: {error}")
            return error
