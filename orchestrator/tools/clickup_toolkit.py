"""
ClickUp Toolkit for Agno Agents
Provides task management capabilities using ClickUp API v2
"""
import os
from typing import Optional, List, Dict, Any
import httpx
from agno.tools import Toolkit
from pydantic import BaseModel, Field


class ClickUpToolkit(Toolkit):
    """
    Agno Toolkit for ClickUp task management.
    
    Provides tools for:
    - Creating tasks
    - Updating task status
    - Getting task lists
    - Adding comments
    - Managing task assignments
    """
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        workspace_id: Optional[str] = None,
        default_list_id: Optional[str] = None
    ):
        super().__init__(name="clickup")
        self.api_token = api_token or os.getenv("CLICKUP_API_TOKEN")
        self.workspace_id = workspace_id or os.getenv("CLICKUP_WORKSPACE_ID")
        self.default_list_id = default_list_id or os.getenv("CLICKUP_DEFAULT_LIST_ID")
        self.base_url = "https://api.clickup.com/api/v2"
        
        if not self.api_token:
            raise ValueError("CLICKUP_API_TOKEN is required")
        
        self.register(self.create_task)
        self.register(self.update_task)
        self.register(self.get_tasks)
        self.register(self.get_task)
        self.register(self.add_comment)
        self.register(self.get_lists)
        self.register(self.move_task_status)
    
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to ClickUp API"""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{self.base_url}{endpoint}",
                headers=self._headers(),
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    def create_task(
        self,
        name: str,
        description: Optional[str] = None,
        priority: int = 3,
        due_date_offset_days: Optional[int] = None,
        tags: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        list_id: Optional[str] = None
    ) -> str:
        """
        Create a new task in ClickUp.
        
        Args:
            name: Task title
            description: Task description (markdown supported)
            priority: 1=Urgent, 2=High, 3=Normal, 4=Low
            due_date_offset_days: Days from now for due date
            tags: List of tag names
            assignees: List of user IDs to assign
            list_id: ClickUp list ID (uses default if not provided)
        
        Returns:
            JSON string with task ID and URL
        """
        import asyncio
        
        target_list = list_id or self.default_list_id
        if not target_list:
            return '{"error": "No list_id provided and no default configured"}'
        
        task_data = {
            "name": name,
            "priority": priority
        }
        
        if description:
            task_data["description"] = description
        if tags:
            task_data["tags"] = tags
        if assignees:
            task_data["assignees"] = assignees
        if due_date_offset_days:
            import time
            task_data["due_date"] = int((time.time() + due_date_offset_days * 86400) * 1000)
        
        try:
            result = asyncio.get_event_loop().run_until_complete(
                self._request("POST", f"/list/{target_list}/task", task_data)
            )
            return f'{{"success": true, "task_id": "{result.get("id")}", "url": "{result.get("url")}"}}'
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def update_task(
        self,
        task_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Update an existing task.
        
        Args:
            task_id: ClickUp task ID
            name: New task name
            description: New description
            priority: New priority (1-4)
            status: New status name
        
        Returns:
            JSON string with success status
        """
        import asyncio
        
        updates = {}
        if name:
            updates["name"] = name
        if description:
            updates["description"] = description
        if priority:
            updates["priority"] = priority
        if status:
            updates["status"] = status
        
        if not updates:
            return '{"error": "No updates provided"}'
        
        try:
            asyncio.get_event_loop().run_until_complete(
                self._request("PUT", f"/task/{task_id}", updates)
            )
            return f'{{"success": true, "task_id": "{task_id}"}}'
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def get_tasks(
        self,
        list_id: Optional[str] = None,
        include_closed: bool = False,
        statuses: Optional[List[str]] = None
    ) -> str:
        """
        Get tasks from a ClickUp list.
        
        Args:
            list_id: ClickUp list ID
            include_closed: Include completed tasks
            statuses: Filter by status names
        
        Returns:
            JSON string with task list
        """
        import asyncio
        
        target_list = list_id or self.default_list_id
        if not target_list:
            return '{"error": "No list_id provided"}'
        
        params = f"?archived=false&include_closed={str(include_closed).lower()}"
        if statuses:
            params += "&" + "&".join([f"statuses[]={s}" for s in statuses])
        
        try:
            result = asyncio.get_event_loop().run_until_complete(
                self._request("GET", f"/list/{target_list}/task{params}")
            )
            tasks = result.get("tasks", [])
            summary = [
                {
                    "id": t["id"],
                    "name": t["name"],
                    "status": t.get("status", {}).get("status"),
                    "priority": t.get("priority", {}).get("priority"),
                    "due_date": t.get("due_date")
                }
                for t in tasks
            ]
            import json
            return json.dumps({"tasks": summary, "count": len(summary)})
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def get_task(self, task_id: str) -> str:
        """
        Get a single task by ID.
        
        Args:
            task_id: ClickUp task ID
        
        Returns:
            JSON string with task details
        """
        import asyncio
        import json
        
        try:
            result = asyncio.get_event_loop().run_until_complete(
                self._request("GET", f"/task/{task_id}")
            )
            return json.dumps({
                "id": result["id"],
                "name": result["name"],
                "description": result.get("description"),
                "status": result.get("status", {}).get("status"),
                "priority": result.get("priority", {}).get("priority"),
                "due_date": result.get("due_date"),
                "url": result.get("url")
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def add_comment(self, task_id: str, comment_text: str) -> str:
        """
        Add a comment to a task.
        
        Args:
            task_id: ClickUp task ID
            comment_text: Comment content
        
        Returns:
            JSON string with success status
        """
        import asyncio
        
        try:
            asyncio.get_event_loop().run_until_complete(
                self._request("POST", f"/task/{task_id}/comment", {"comment_text": comment_text})
            )
            return f'{{"success": true, "task_id": "{task_id}"}}'
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def get_lists(self, folder_id: Optional[str] = None, space_id: Optional[str] = None) -> str:
        """
        Get lists from a folder or space.
        
        Args:
            folder_id: ClickUp folder ID
            space_id: ClickUp space ID (for folderless lists)
        
        Returns:
            JSON string with list information
        """
        import asyncio
        import json
        
        try:
            if folder_id:
                result = asyncio.get_event_loop().run_until_complete(
                    self._request("GET", f"/folder/{folder_id}/list")
                )
            elif space_id:
                result = asyncio.get_event_loop().run_until_complete(
                    self._request("GET", f"/space/{space_id}/list")
                )
            else:
                return '{"error": "Either folder_id or space_id required"}'
            
            lists = [{"id": l["id"], "name": l["name"]} for l in result.get("lists", [])]
            return json.dumps({"lists": lists})
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def move_task_status(self, task_id: str, new_status: str) -> str:
        """
        Move a task to a new status.
        
        Args:
            task_id: ClickUp task ID
            new_status: Status name to move to
        
        Returns:
            JSON string with success status
        """
        return self.update_task(task_id, status=new_status)
