from googleapiclient.discovery import build


def build_service(creds):
    return build('sheets', 'v4', credentials=creds)


class SheetsApi:
    def __init__(self, creds):
        self.service = build_service(creds)

    def get_sheet(self, sheet_id):
        sheet = self.service.spreadsheets()
        return sheet.get(spreadsheetId=sheet_id).execute()
    
    def get_range(self, sheet_id, range_id):
        return self.service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_id).execute()
