"""
Google Docs API Client for Marketing Plan Export

Requires:
- google-auth
- google-auth-oauthlib  
- google-api-python-client

Set GOOGLE_SERVICE_ACCOUNT_JSON env var with service account credentials JSON.
"""
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from lib.logging_config import logger


class GoogleDocsClient:
    """Client for creating and managing Google Docs"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self):
        self.available = False
        self.docs_service = None
        self.drive_service = None
        
        if not GOOGLE_AVAILABLE:
            logger.warning("Google API libraries not installed")
            return
        
        # Try to load service account credentials
        creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not creds_json:
            logger.warning("GOOGLE_SERVICE_ACCOUNT_JSON not set")
            return
        
        try:
            creds_dict = json.loads(creds_json)
            credentials = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=self.SCOPES
            )
            self.docs_service = build('docs', 'v1', credentials=credentials)
            self.drive_service = build('drive', 'v3', credentials=credentials)
            self.available = True
            logger.info("Google Docs client initialized")
        except Exception as e:
            logger.error("Failed to initialize Google Docs client", error=str(e))
    
    def create_document(self, title: str, content: str, folder_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Google Doc with the given content.
        
        Args:
            title: Document title
            content: Markdown or plain text content
            folder_id: Optional Google Drive folder ID to place the doc in
            
        Returns:
            Dict with document_id, document_url, title
        """
        if not self.available:
            raise RuntimeError("Google Docs client not available")
        
        try:
            # Create the document
            doc = self.docs_service.documents().create(body={'title': title}).execute()
            document_id = doc.get('documentId')
            
            # Insert content
            requests = self._build_insert_requests(content)
            if requests:
                self.docs_service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': requests}
                ).execute()
            
            # Move to folder if specified
            if folder_id:
                self._move_to_folder(document_id, folder_id)
            
            document_url = f"https://docs.google.com/document/d/{document_id}/edit"
            
            logger.info("Created Google Doc", title=title, document_id=document_id)
            
            return {
                "document_id": document_id,
                "document_url": document_url,
                "title": title
            }
            
        except HttpError as e:
            logger.error("Google Docs API error", error=str(e))
            raise RuntimeError(f"Failed to create document: {e}")
    
    def _build_insert_requests(self, content: str) -> list:
        """Build batch update requests for inserting formatted content"""
        requests = []
        
        # For now, insert as plain text
        # Future: Parse markdown and apply formatting
        if content:
            requests.append({
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            })
        
        return requests
    
    def _move_to_folder(self, file_id: str, folder_id: str):
        """Move a file to a specific folder"""
        try:
            # Get current parents
            file = self.drive_service.files().get(
                fileId=file_id, fields='parents'
            ).execute()
            previous_parents = ",".join(file.get('parents', []))
            
            # Move to new folder
            self.drive_service.files().update(
                fileId=file_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
        except HttpError as e:
            logger.warning("Could not move to folder", error=str(e))
    
    def share_document(self, document_id: str, email: Optional[str] = None, anyone_with_link: bool = True) -> bool:
        """
        Share a document with a user or make it accessible via link.
        
        Args:
            document_id: The Google Doc ID
            email: Email address to share with (optional)
            anyone_with_link: If True, make document accessible to anyone with link
            
        Returns:
            True if sharing succeeded
        """
        if not self.available:
            return False
        
        try:
            if anyone_with_link:
                # Make document accessible to anyone with the link
                permission = {
                    'type': 'anyone',
                    'role': 'reader'  # or 'writer' for edit access
                }
                self.drive_service.permissions().create(
                    fileId=document_id,
                    body=permission,
                    fields='id'
                ).execute()
                logger.info("Shared document with anyone with link", document_id=document_id)
            
            if email:
                # Share with specific user
                permission = {
                    'type': 'user',
                    'role': 'writer',
                    'emailAddress': email
                }
                self.drive_service.permissions().create(
                    fileId=document_id,
                    body=permission,
                    sendNotificationEmail=True,
                    fields='id'
                ).execute()
                logger.info("Shared document with user", document_id=document_id, email=email)
            
            return True
            
        except HttpError as e:
            logger.error("Failed to share document", error=str(e), document_id=document_id)
            return False
    
    def create_and_share_document(
        self, 
        title: str, 
        content: str, 
        folder_id: Optional[str] = None,
        share_email: Optional[str] = None,
        public_link: bool = True
    ) -> Dict[str, Any]:
        """
        Create a document and share it in one operation.
        
        Args:
            title: Document title
            content: Document content (markdown or plain text)
            folder_id: Optional folder to place document in
            share_email: Optional email to share with
            public_link: If True, make accessible to anyone with link
            
        Returns:
            Dict with document_id, document_url, title, shared
        """
        result = self.create_document(title, content, folder_id)
        
        # Share the document
        shared = self.share_document(
            result['document_id'], 
            email=share_email, 
            anyone_with_link=public_link
        )
        result['shared'] = shared
        
        return result


# Singleton instance
_google_docs_client: Optional[GoogleDocsClient] = None


def get_google_docs_client() -> GoogleDocsClient:
    """Get or create Google Docs client instance"""
    global _google_docs_client
    if _google_docs_client is None:
        _google_docs_client = GoogleDocsClient()
    return _google_docs_client
