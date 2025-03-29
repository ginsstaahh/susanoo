from googleapiclient.errors import HttpError
from dags.helpers.google import sheets_service, drive_service


def create(title, folder_id):
    """
    Creates the Sheet the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    # pylint: disable=maybe-no-member
    try:
        spreadsheet = {"properties": {"title": title}}
        spreadsheet = (
            sheets_service.spreadsheets()
            .create(body=spreadsheet, fields="spreadsheetId")
            .execute()
        )
        print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")

        # Move the spreadsheet to the designated folder on Google Drive.
        sheet_id = spreadsheet.get("spreadsheetId")
        file = drive_service.files().get(fileId=sheet_id, fields="parents").execute()
        previous_parents = ",".join(file.get("parents"))
        drive_service.files().update(fileId=sheet_id, addParents=folder_id, removeParents=previous_parents, fields='id, parents').execute()

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


if __name__ == "__main__":
  # create sheets with title and directory
  spreadsheet_title = 'weather and pollution datasets'
  susanoo_folder_id = '1P-i6M3rzo8fE_RnyVH_Pisla8F2l4aDM'
  create(spreadsheet_title, susanoo_folder_id)