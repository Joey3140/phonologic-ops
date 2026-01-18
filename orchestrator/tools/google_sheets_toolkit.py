"""
Google Sheets Toolkit for Agno Agents
Provides spreadsheet reading, writing, and data manipulation capabilities
"""
import os
import json
from typing import Optional, List, Dict, Any, Union
from agno.tools import Toolkit


class GoogleSheetsToolkit(Toolkit):
    """
    Agno Toolkit for Google Sheets operations.
    
    Provides tools for:
    - Reading spreadsheet data
    - Writing/updating cells and ranges
    - Creating new spreadsheets
    - Managing sheets within a spreadsheet
    - Formatting and formulas
    """
    
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        service_account_json: Optional[str] = None,
        default_folder_id: Optional[str] = None
    ):
        super().__init__(name="google_sheets")
        self.credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.service_account_json = service_account_json or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        self.default_folder_id = default_folder_id or os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        self._sheets_service = None
        self._drive_service = None
        
        self.register(self.read_spreadsheet)
        self.register(self.read_range)
        self.register(self.write_range)
        self.register(self.append_rows)
        self.register(self.create_spreadsheet)
        self.register(self.get_spreadsheet_info)
        self.register(self.add_sheet)
        self.register(self.clear_range)
    
    def _get_services(self):
        """Initialize Google Sheets and Drive services"""
        if self._sheets_service is None:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            if self.service_account_json:
                creds_dict = json.loads(self.service_account_json)
                credentials = service_account.Credentials.from_service_account_info(
                    creds_dict,
                    scopes=scopes
                )
            elif self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=scopes
                )
            else:
                raise ValueError("Google credentials not configured")
            
            self._sheets_service = build('sheets', 'v4', credentials=credentials)
            self._drive_service = build('drive', 'v3', credentials=credentials)
        
        return self._sheets_service, self._drive_service
    
    def read_spreadsheet(
        self,
        spreadsheet_id: str,
        sheet_name: Optional[str] = None,
        include_headers: bool = True
    ) -> str:
        """
        Read all data from a spreadsheet or specific sheet.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet_name: Specific sheet name (reads first sheet if not provided)
            include_headers: Whether to treat first row as headers
        
        Returns:
            JSON string with spreadsheet data
        """
        try:
            sheets_service, _ = self._get_services()
            
            if sheet_name:
                range_notation = f"'{sheet_name}'"
            else:
                metadata = sheets_service.spreadsheets().get(
                    spreadsheetId=spreadsheet_id
                ).execute()
                first_sheet = metadata['sheets'][0]['properties']['title']
                range_notation = f"'{first_sheet}'"
            
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_notation
            ).execute()
            
            values = result.get('values', [])
            
            if include_headers and len(values) > 0:
                headers = values[0]
                rows = []
                for row in values[1:]:
                    row_dict = {}
                    for i, header in enumerate(headers):
                        row_dict[header] = row[i] if i < len(row) else ""
                    rows.append(row_dict)
                return json.dumps({
                    "headers": headers,
                    "rows": rows,
                    "row_count": len(rows)
                })
            else:
                return json.dumps({
                    "data": values,
                    "row_count": len(values)
                })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def read_range(
        self,
        spreadsheet_id: str,
        range_notation: str
    ) -> str:
        """
        Read data from a specific range (e.g., 'Sheet1!A1:D10').
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            range_notation: A1 notation range (e.g., 'Sheet1!A1:D10')
        
        Returns:
            JSON string with range data
        """
        try:
            sheets_service, _ = self._get_services()
            
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_notation
            ).execute()
            
            values = result.get('values', [])
            return json.dumps({
                "range": range_notation,
                "data": values,
                "row_count": len(values),
                "col_count": max(len(row) for row in values) if values else 0
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def write_range(
        self,
        spreadsheet_id: str,
        range_notation: str,
        values: List[List[Any]],
        value_input_option: str = "USER_ENTERED"
    ) -> str:
        """
        Write data to a specific range.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            range_notation: A1 notation range (e.g., 'Sheet1!A1:D10')
            values: 2D array of values to write
            value_input_option: How to interpret values ('RAW' or 'USER_ENTERED')
        
        Returns:
            JSON string with update result
        """
        try:
            sheets_service, _ = self._get_services()
            
            body = {'values': values}
            
            result = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_notation,
                valueInputOption=value_input_option,
                body=body
            ).execute()
            
            return json.dumps({
                "success": True,
                "updated_range": result.get('updatedRange'),
                "updated_rows": result.get('updatedRows'),
                "updated_columns": result.get('updatedColumns'),
                "updated_cells": result.get('updatedCells')
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def append_rows(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        rows: List[List[Any]],
        value_input_option: str = "USER_ENTERED"
    ) -> str:
        """
        Append rows to the end of a sheet.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet_name: Name of the sheet to append to
            rows: 2D array of rows to append
            value_input_option: How to interpret values ('RAW' or 'USER_ENTERED')
        
        Returns:
            JSON string with append result
        """
        try:
            sheets_service, _ = self._get_services()
            
            body = {'values': rows}
            
            result = sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"'{sheet_name}'",
                valueInputOption=value_input_option,
                insertDataOption="INSERT_ROWS",
                body=body
            ).execute()
            
            return json.dumps({
                "success": True,
                "updated_range": result.get('updates', {}).get('updatedRange'),
                "appended_rows": len(rows)
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def create_spreadsheet(
        self,
        title: str,
        sheet_names: Optional[List[str]] = None,
        folder_id: Optional[str] = None
    ) -> str:
        """
        Create a new Google Spreadsheet.
        
        Args:
            title: Title for the new spreadsheet
            sheet_names: Optional list of sheet names to create
            folder_id: Drive folder ID to place the spreadsheet
        
        Returns:
            JSON string with new spreadsheet info
        """
        try:
            sheets_service, drive_service = self._get_services()
            
            sheets = []
            if sheet_names:
                for i, name in enumerate(sheet_names):
                    sheets.append({
                        'properties': {
                            'sheetId': i,
                            'title': name
                        }
                    })
            
            body = {
                'properties': {'title': title}
            }
            if sheets:
                body['sheets'] = sheets
            
            spreadsheet = sheets_service.spreadsheets().create(body=body).execute()
            spreadsheet_id = spreadsheet['spreadsheetId']
            
            target_folder = folder_id or self.default_folder_id
            if target_folder:
                file = drive_service.files().get(
                    fileId=spreadsheet_id,
                    fields='parents'
                ).execute()
                
                previous_parents = ",".join(file.get('parents', []))
                drive_service.files().update(
                    fileId=spreadsheet_id,
                    addParents=target_folder,
                    removeParents=previous_parents,
                    fields='id, parents'
                ).execute()
            
            return json.dumps({
                "success": True,
                "id": spreadsheet_id,
                "title": title,
                "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
                "sheets": [s['properties']['title'] for s in spreadsheet.get('sheets', [])]
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def get_spreadsheet_info(self, spreadsheet_id: str) -> str:
        """
        Get metadata about a spreadsheet including all sheet names.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
        
        Returns:
            JSON string with spreadsheet metadata
        """
        try:
            sheets_service, _ = self._get_services()
            
            metadata = sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheets_info = []
            for sheet in metadata.get('sheets', []):
                props = sheet['properties']
                sheets_info.append({
                    "id": props['sheetId'],
                    "title": props['title'],
                    "index": props['index'],
                    "row_count": props.get('gridProperties', {}).get('rowCount'),
                    "column_count": props.get('gridProperties', {}).get('columnCount')
                })
            
            return json.dumps({
                "id": spreadsheet_id,
                "title": metadata['properties']['title'],
                "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
                "sheets": sheets_info,
                "locale": metadata['properties'].get('locale'),
                "time_zone": metadata['properties'].get('timeZone')
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def add_sheet(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        row_count: int = 1000,
        column_count: int = 26
    ) -> str:
        """
        Add a new sheet to an existing spreadsheet.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet_name: Name for the new sheet
            row_count: Initial number of rows
            column_count: Initial number of columns
        
        Returns:
            JSON string with new sheet info
        """
        try:
            sheets_service, _ = self._get_services()
            
            request = {
                'addSheet': {
                    'properties': {
                        'title': sheet_name,
                        'gridProperties': {
                            'rowCount': row_count,
                            'columnCount': column_count
                        }
                    }
                }
            }
            
            result = sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': [request]}
            ).execute()
            
            reply = result.get('replies', [{}])[0].get('addSheet', {})
            props = reply.get('properties', {})
            
            return json.dumps({
                "success": True,
                "sheet_id": props.get('sheetId'),
                "title": props.get('title'),
                "index": props.get('index')
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def clear_range(
        self,
        spreadsheet_id: str,
        range_notation: str
    ) -> str:
        """
        Clear all values from a range (preserves formatting).
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            range_notation: A1 notation range to clear
        
        Returns:
            JSON string with clear result
        """
        try:
            sheets_service, _ = self._get_services()
            
            result = sheets_service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_notation
            ).execute()
            
            return json.dumps({
                "success": True,
                "cleared_range": result.get('clearedRange')
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
