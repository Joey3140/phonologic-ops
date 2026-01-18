"""
Google Slides Toolkit for Agno Agents
Provides presentation reading, creation, and manipulation capabilities
"""
import os
import json
from typing import Optional, List, Dict, Any
from agno.tools import Toolkit


class GoogleSlidesToolkit(Toolkit):
    """
    Agno Toolkit for Google Slides operations.
    
    Provides tools for:
    - Reading presentation content
    - Creating presentations
    - Adding and modifying slides
    - Text replacement and template filling
    - Inserting images and shapes
    """
    
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        service_account_json: Optional[str] = None,
        default_folder_id: Optional[str] = None
    ):
        super().__init__(name="google_slides")
        self.credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.service_account_json = service_account_json or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        self.default_folder_id = default_folder_id or os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        self._slides_service = None
        self._drive_service = None
        
        self.register(self.get_presentation_info)
        self.register(self.read_slide)
        self.register(self.read_all_text)
        self.register(self.create_presentation)
        self.register(self.add_slide)
        self.register(self.replace_text)
        self.register(self.fill_template)
        self.register(self.insert_image)
    
    def _get_services(self):
        """Initialize Google Slides and Drive services"""
        if self._slides_service is None:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            scopes = [
                'https://www.googleapis.com/auth/presentations',
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
            
            self._slides_service = build('slides', 'v1', credentials=credentials)
            self._drive_service = build('drive', 'v3', credentials=credentials)
        
        return self._slides_service, self._drive_service
    
    def get_presentation_info(self, presentation_id: str) -> str:
        """
        Get metadata about a presentation including all slide IDs.
        
        Args:
            presentation_id: Google Slides presentation ID
        
        Returns:
            JSON string with presentation metadata
        """
        try:
            slides_service, _ = self._get_services()
            
            presentation = slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            slides_info = []
            for i, slide in enumerate(presentation.get('slides', [])):
                slide_info = {
                    "index": i,
                    "id": slide['objectId'],
                    "layout": slide.get('slideProperties', {}).get('layoutObjectId')
                }
                slides_info.append(slide_info)
            
            return json.dumps({
                "id": presentation_id,
                "title": presentation.get('title', ''),
                "url": f"https://docs.google.com/presentation/d/{presentation_id}/edit",
                "slide_count": len(slides_info),
                "slides": slides_info,
                "page_size": presentation.get('pageSize', {})
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def read_slide(
        self,
        presentation_id: str,
        slide_index: int = 0
    ) -> str:
        """
        Read content from a specific slide by index.
        
        Args:
            presentation_id: Google Slides presentation ID
            slide_index: 0-based slide index
        
        Returns:
            JSON string with slide content
        """
        try:
            slides_service, _ = self._get_services()
            
            presentation = slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            slides = presentation.get('slides', [])
            if slide_index >= len(slides):
                return json.dumps({"error": f"Slide index {slide_index} out of range (0-{len(slides)-1})"})
            
            slide = slides[slide_index]
            elements = []
            
            for element in slide.get('pageElements', []):
                elem_info = {
                    "id": element['objectId'],
                    "type": self._get_element_type(element)
                }
                
                if 'shape' in element and 'text' in element['shape']:
                    text_content = self._extract_text(element['shape']['text'])
                    if text_content:
                        elem_info['text'] = text_content
                
                if 'image' in element:
                    elem_info['image_url'] = element['image'].get('sourceUrl')
                
                if 'transform' in element:
                    elem_info['position'] = {
                        'x': element['transform'].get('translateX', 0),
                        'y': element['transform'].get('translateY', 0)
                    }
                
                elements.append(elem_info)
            
            return json.dumps({
                "slide_index": slide_index,
                "slide_id": slide['objectId'],
                "element_count": len(elements),
                "elements": elements
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def _get_element_type(self, element: Dict) -> str:
        """Determine the type of page element"""
        if 'shape' in element:
            return element['shape'].get('shapeType', 'SHAPE')
        elif 'image' in element:
            return 'IMAGE'
        elif 'table' in element:
            return 'TABLE'
        elif 'line' in element:
            return 'LINE'
        elif 'video' in element:
            return 'VIDEO'
        elif 'elementGroup' in element:
            return 'GROUP'
        return 'UNKNOWN'
    
    def _extract_text(self, text_obj: Dict) -> str:
        """Extract plain text from a text object"""
        text_parts = []
        for element in text_obj.get('textElements', []):
            if 'textRun' in element:
                text_parts.append(element['textRun'].get('content', ''))
        return ''.join(text_parts).strip()
    
    def read_all_text(self, presentation_id: str) -> str:
        """
        Extract all text content from a presentation.
        
        Args:
            presentation_id: Google Slides presentation ID
        
        Returns:
            JSON string with all text organized by slide
        """
        try:
            slides_service, _ = self._get_services()
            
            presentation = slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            slides_text = []
            for i, slide in enumerate(presentation.get('slides', [])):
                slide_texts = []
                for element in slide.get('pageElements', []):
                    if 'shape' in element and 'text' in element['shape']:
                        text = self._extract_text(element['shape']['text'])
                        if text:
                            slide_texts.append(text)
                
                slides_text.append({
                    "slide_index": i,
                    "slide_id": slide['objectId'],
                    "texts": slide_texts
                })
            
            return json.dumps({
                "title": presentation.get('title', ''),
                "slide_count": len(slides_text),
                "slides": slides_text
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def create_presentation(
        self,
        title: str,
        folder_id: Optional[str] = None
    ) -> str:
        """
        Create a new Google Slides presentation.
        
        Args:
            title: Title for the new presentation
            folder_id: Drive folder ID to place the presentation
        
        Returns:
            JSON string with new presentation info
        """
        try:
            slides_service, drive_service = self._get_services()
            
            presentation = slides_service.presentations().create(
                body={'title': title}
            ).execute()
            
            presentation_id = presentation['presentationId']
            
            target_folder = folder_id or self.default_folder_id
            if target_folder:
                file = drive_service.files().get(
                    fileId=presentation_id,
                    fields='parents'
                ).execute()
                
                previous_parents = ",".join(file.get('parents', []))
                drive_service.files().update(
                    fileId=presentation_id,
                    addParents=target_folder,
                    removeParents=previous_parents,
                    fields='id, parents'
                ).execute()
            
            return json.dumps({
                "success": True,
                "id": presentation_id,
                "title": title,
                "url": f"https://docs.google.com/presentation/d/{presentation_id}/edit"
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def add_slide(
        self,
        presentation_id: str,
        layout: str = "BLANK",
        insert_at: Optional[int] = None
    ) -> str:
        """
        Add a new slide to a presentation.
        
        Args:
            presentation_id: Google Slides presentation ID
            layout: Layout type (BLANK, TITLE, TITLE_AND_BODY, TITLE_AND_TWO_COLUMNS, etc.)
            insert_at: Optional 0-based index to insert slide at
        
        Returns:
            JSON string with new slide info
        """
        try:
            slides_service, _ = self._get_services()
            
            layout_mapping = {
                'BLANK': 'BLANK',
                'TITLE': 'TITLE',
                'TITLE_AND_BODY': 'TITLE_AND_BODY',
                'TITLE_AND_TWO_COLUMNS': 'TITLE_AND_TWO_COLUMNS',
                'TITLE_ONLY': 'TITLE_ONLY',
                'SECTION_HEADER': 'SECTION_HEADER',
                'SECTION_TITLE_AND_DESCRIPTION': 'SECTION_TITLE_AND_DESCRIPTION',
                'ONE_COLUMN_TEXT': 'ONE_COLUMN_TEXT',
                'MAIN_POINT': 'MAIN_POINT',
                'BIG_NUMBER': 'BIG_NUMBER'
            }
            
            predefined_layout = layout_mapping.get(layout.upper(), 'BLANK')
            
            request = {
                'createSlide': {
                    'slideLayoutReference': {
                        'predefinedLayout': predefined_layout
                    }
                }
            }
            
            if insert_at is not None:
                request['createSlide']['insertionIndex'] = insert_at
            
            result = slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': [request]}
            ).execute()
            
            reply = result.get('replies', [{}])[0].get('createSlide', {})
            
            return json.dumps({
                "success": True,
                "slide_id": reply.get('objectId'),
                "layout": predefined_layout
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def replace_text(
        self,
        presentation_id: str,
        find_text: str,
        replace_text: str,
        match_case: bool = True
    ) -> str:
        """
        Find and replace text across the entire presentation.
        
        Args:
            presentation_id: Google Slides presentation ID
            find_text: Text to find
            replace_text: Text to replace with
            match_case: Whether to match case
        
        Returns:
            JSON string with replacement result
        """
        try:
            slides_service, _ = self._get_services()
            
            request = {
                'replaceAllText': {
                    'containsText': {
                        'text': find_text,
                        'matchCase': match_case
                    },
                    'replaceText': replace_text
                }
            }
            
            result = slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': [request]}
            ).execute()
            
            reply = result.get('replies', [{}])[0].get('replaceAllText', {})
            
            return json.dumps({
                "success": True,
                "occurrences_replaced": reply.get('occurrencesChanged', 0)
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
        Create a presentation from a template by replacing placeholders.
        
        Args:
            template_id: Google Slides template presentation ID
            placeholders: Dictionary of {{placeholder}}: value pairs
            output_name: Name for the generated presentation
            output_folder_id: Folder for the output presentation
        
        Returns:
            JSON string with new presentation info
        """
        try:
            slides_service, drive_service = self._get_services()
            
            target_folder = output_folder_id or self.default_folder_id
            
            copy_metadata = {'name': output_name}
            if target_folder:
                copy_metadata['parents'] = [target_folder]
            
            copied_file = drive_service.files().copy(
                fileId=template_id,
                body=copy_metadata
            ).execute()
            
            new_presentation_id = copied_file['id']
            
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
                slides_service.presentations().batchUpdate(
                    presentationId=new_presentation_id,
                    body={'requests': requests}
                ).execute()
            
            return json.dumps({
                "success": True,
                "id": new_presentation_id,
                "name": output_name,
                "url": f"https://docs.google.com/presentation/d/{new_presentation_id}/edit",
                "placeholders_filled": len(placeholders)
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def insert_image(
        self,
        presentation_id: str,
        slide_id: str,
        image_url: str,
        width: float = 300,
        height: float = 200,
        x: float = 100,
        y: float = 100
    ) -> str:
        """
        Insert an image into a slide.
        
        Args:
            presentation_id: Google Slides presentation ID
            slide_id: ID of the slide to insert into
            image_url: Public URL of the image
            width: Image width in points
            height: Image height in points
            x: X position in points
            y: Y position in points
        
        Returns:
            JSON string with insert result
        """
        try:
            slides_service, _ = self._get_services()
            
            import uuid
            image_id = f"image_{uuid.uuid4().hex[:8]}"
            
            request = {
                'createImage': {
                    'objectId': image_id,
                    'url': image_url,
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': width, 'unit': 'PT'},
                            'height': {'magnitude': height, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': x,
                            'translateY': y,
                            'unit': 'PT'
                        }
                    }
                }
            }
            
            result = slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': [request]}
            ).execute()
            
            return json.dumps({
                "success": True,
                "image_id": image_id,
                "slide_id": slide_id
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
