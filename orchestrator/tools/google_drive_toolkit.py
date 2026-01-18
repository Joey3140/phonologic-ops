"""
Google Drive Toolkit for Agno Agents
Provides document management and template filling capabilities
"""
import os
import json
from typing import Optional, List, Dict, Any
from agno.tools import Toolkit


class GoogleDriveToolkit(Toolkit):
    """
    Agno Toolkit for Google Drive operations.
    
    Provides tools for:
    - Listing files and folders
    - Reading document content
    - Creating documents from templates
    - Filling template placeholders
    - Uploading files
    """
    
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        service_account_json: Optional[str] = None,
        default_folder_id: Optional[str] = None
    ):
        super().__init__(name="google_drive")
        self.credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.service_account_json = service_account_json or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        self.default_folder_id = default_folder_id or os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        self._service = None
        self._docs_service = None
        
        self.register(self.list_files)
        self.register(self.get_file_info)
        self.register(self.read_document)
        self.register(self.copy_file)
        self.register(self.fill_template)
        self.register(self.create_folder)
    
    def _get_drive_service(self):
        """Initialize Google Drive service"""
        if self._service is None:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            if self.service_account_json:
                creds_dict = json.loads(self.service_account_json)
                credentials = service_account.Credentials.from_service_account_info(
                    creds_dict,
                    scopes=[
                        'https://www.googleapis.com/auth/drive',
                        'https://www.googleapis.com/auth/documents'
                    ]
                )
            elif self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=[
                        'https://www.googleapis.com/auth/drive',
                        'https://www.googleapis.com/auth/documents'
                    ]
                )
            else:
                raise ValueError("Google credentials not configured")
            
            self._service = build('drive', 'v3', credentials=credentials)
            self._docs_service = build('docs', 'v1', credentials=credentials)
        
        return self._service, self._docs_service
    
    def list_files(
        self,
        folder_id: Optional[str] = None,
        file_type: Optional[str] = None,
        max_results: int = 20
    ) -> str:
        """
        List files in a Google Drive folder.
        
        Args:
            folder_id: Drive folder ID (uses default if not provided)
            file_type: Filter by MIME type (e.g., 'document', 'spreadsheet', 'folder')
            max_results: Maximum number of files to return
        
        Returns:
            JSON string with file list
        """
        try:
            drive_service, _ = self._get_drive_service()
            target_folder = folder_id or self.default_folder_id
            
            query_parts = []
            if target_folder:
                query_parts.append(f"'{target_folder}' in parents")
            query_parts.append("trashed = false")
            
            if file_type:
                mime_types = {
                    'document': 'application/vnd.google-apps.document',
                    'spreadsheet': 'application/vnd.google-apps.spreadsheet',
                    'presentation': 'application/vnd.google-apps.presentation',
                    'folder': 'application/vnd.google-apps.folder',
                    'pdf': 'application/pdf'
                }
                if file_type in mime_types:
                    query_parts.append(f"mimeType = '{mime_types[file_type]}'")
            
            query = " and ".join(query_parts)
            
            results = drive_service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, mimeType, webViewLink, createdTime, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            return json.dumps({
                "files": [
                    {
                        "id": f["id"],
                        "name": f["name"],
                        "type": f["mimeType"].split('.')[-1] if 'google-apps' in f["mimeType"] else f["mimeType"],
                        "url": f.get("webViewLink"),
                        "modified": f.get("modifiedTime")
                    }
                    for f in files
                ],
                "count": len(files)
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def get_file_info(self, file_id: str) -> str:
        """
        Get metadata for a specific file.
        
        Args:
            file_id: Google Drive file ID
        
        Returns:
            JSON string with file metadata
        """
        try:
            drive_service, _ = self._get_drive_service()
            
            file_metadata = drive_service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, webViewLink, createdTime, modifiedTime, size, owners"
            ).execute()
            
            return json.dumps({
                "id": file_metadata["id"],
                "name": file_metadata["name"],
                "type": file_metadata["mimeType"],
                "url": file_metadata.get("webViewLink"),
                "created": file_metadata.get("createdTime"),
                "modified": file_metadata.get("modifiedTime"),
                "size": file_metadata.get("size"),
                "owners": [o.get("emailAddress") for o in file_metadata.get("owners", [])]
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def read_document(self, document_id: str) -> str:
        """
        Read the text content of a Google Doc.
        
        Args:
            document_id: Google Docs document ID
        
        Returns:
            JSON string with document title and content
        """
        try:
            _, docs_service = self._get_drive_service()
            
            doc = docs_service.documents().get(documentId=document_id).execute()
            
            content_parts = []
            for element in doc.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for text_run in element['paragraph'].get('elements', []):
                        if 'textRun' in text_run:
                            content_parts.append(text_run['textRun'].get('content', ''))
            
            return json.dumps({
                "id": doc["documentId"],
                "title": doc.get("title", ""),
                "content": "".join(content_parts)
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def copy_file(
        self,
        source_file_id: str,
        new_name: str,
        destination_folder_id: Optional[str] = None
    ) -> str:
        """
        Copy a file to create a new document.
        
        Args:
            source_file_id: ID of the file to copy
            new_name: Name for the new file
            destination_folder_id: Folder to place the copy
        
        Returns:
            JSON string with new file info
        """
        try:
            drive_service, _ = self._get_drive_service()
            
            body = {"name": new_name}
            if destination_folder_id:
                body["parents"] = [destination_folder_id]
            
            copied_file = drive_service.files().copy(
                fileId=source_file_id,
                body=body
            ).execute()
            
            return json.dumps({
                "success": True,
                "id": copied_file["id"],
                "name": copied_file["name"],
                "url": f"https://docs.google.com/document/d/{copied_file['id']}/edit"
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def fill_template(
        self,
        template_id: str,
        placeholders: Dict[str, str],
        output_name: str,
        output_folder_id: Optional[str] = None
    ) -> str:
        """
        Create a document from a template by replacing placeholders.
        
        Args:
            template_id: Google Docs template ID
            placeholders: Dictionary of {{placeholder}}: value pairs
            output_name: Name for the generated document
            output_folder_id: Folder for the output document
        
        Returns:
            JSON string with new document info
        """
        try:
            drive_service, docs_service = self._get_drive_service()
            
            copy_result = json.loads(self.copy_file(
                template_id, 
                output_name, 
                output_folder_id or self.default_folder_id
            ))
            
            if "error" in copy_result:
                return json.dumps(copy_result)
            
            new_doc_id = copy_result["id"]
            
            requests = []
            for placeholder, value in placeholders.items():
                search_text = f"{{{{{placeholder}}}}}"
                requests.append({
                    'replaceAllText': {
                        'containsText': {
                            'text': search_text,
                            'matchCase': True
                        },
                        'replaceText': value
                    }
                })
            
            if requests:
                docs_service.documents().batchUpdate(
                    documentId=new_doc_id,
                    body={'requests': requests}
                ).execute()
            
            return json.dumps({
                "success": True,
                "id": new_doc_id,
                "name": output_name,
                "url": f"https://docs.google.com/document/d/{new_doc_id}/edit",
                "placeholders_filled": len(placeholders)
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def create_folder(
        self,
        folder_name: str,
        parent_folder_id: Optional[str] = None
    ) -> str:
        """
        Create a new folder in Google Drive.
        
        Args:
            folder_name: Name for the new folder
            parent_folder_id: Parent folder ID
        
        Returns:
            JSON string with new folder info
        """
        try:
            drive_service, _ = self._get_drive_service()
            
            metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                metadata['parents'] = [parent_folder_id]
            elif self.default_folder_id:
                metadata['parents'] = [self.default_folder_id]
            
            folder = drive_service.files().create(
                body=metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            return json.dumps({
                "success": True,
                "id": folder["id"],
                "name": folder["name"],
                "url": folder.get("webViewLink")
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
