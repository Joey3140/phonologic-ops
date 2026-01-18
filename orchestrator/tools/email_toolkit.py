"""
Email Toolkit for Agno Agents
Provides email capabilities using SendGrid
"""
import os
import json
from typing import Optional, List, Dict, Any
from agno.tools import Toolkit


class EmailToolkit(Toolkit):
    """
    Agno Toolkit for sending emails via SendGrid.
    
    Provides tools for:
    - Sending plain text emails
    - Sending HTML emails
    - Sending templated emails
    - Sending emails with attachments
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ):
        super().__init__(name="email")
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")
        self.from_email = from_email or os.getenv("SENDGRID_FROM_EMAIL", "ops@phonologic.ca")
        self.from_name = from_name or os.getenv("SENDGRID_FROM_NAME", "Phonologic Operations")
        
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY is required")
        
        self.register(self.send_email)
        self.register(self.send_html_email)
        self.register(self.send_template_email)
    
    def _get_client(self):
        """Get SendGrid client"""
        from sendgrid import SendGridAPIClient
        return SendGridAPIClient(self.api_key)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        to_name: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None
    ) -> str:
        """
        Send a plain text email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Plain text email body
            to_name: Recipient name (optional)
            cc_emails: List of CC email addresses
            bcc_emails: List of BCC email addresses
        
        Returns:
            JSON string with send status
        """
        try:
            from sendgrid.helpers.mail import Mail, To, Cc, Bcc
            
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=To(to_email, to_name) if to_name else to_email,
                subject=subject,
                plain_text_content=body
            )
            
            if cc_emails:
                for cc in cc_emails:
                    message.add_cc(Cc(cc))
            
            if bcc_emails:
                for bcc in bcc_emails:
                    message.add_bcc(Bcc(bcc))
            
            client = self._get_client()
            response = client.send(message)
            
            return json.dumps({
                "success": True,
                "status_code": response.status_code,
                "message_id": response.headers.get('X-Message-Id'),
                "to": to_email
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def send_html_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        plain_text_body: Optional[str] = None,
        to_name: Optional[str] = None
    ) -> str:
        """
        Send an HTML email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_body: HTML email body
            plain_text_body: Plain text fallback (optional)
            to_name: Recipient name (optional)
        
        Returns:
            JSON string with send status
        """
        try:
            from sendgrid.helpers.mail import Mail, To
            
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=To(to_email, to_name) if to_name else to_email,
                subject=subject,
                html_content=html_body
            )
            
            if plain_text_body:
                message.plain_text_content = plain_text_body
            
            client = self._get_client()
            response = client.send(message)
            
            return json.dumps({
                "success": True,
                "status_code": response.status_code,
                "message_id": response.headers.get('X-Message-Id'),
                "to": to_email
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def send_template_email(
        self,
        to_email: str,
        template_id: str,
        template_data: Dict[str, Any],
        subject: Optional[str] = None,
        to_name: Optional[str] = None
    ) -> str:
        """
        Send an email using a SendGrid dynamic template.
        
        Args:
            to_email: Recipient email address
            template_id: SendGrid template ID
            template_data: Dynamic template data dictionary
            subject: Subject override (optional, uses template default)
            to_name: Recipient name (optional)
        
        Returns:
            JSON string with send status
        """
        try:
            from sendgrid.helpers.mail import Mail, To
            
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=To(to_email, to_name) if to_name else to_email
            )
            
            if subject:
                message.subject = subject
            
            message.template_id = template_id
            message.dynamic_template_data = template_data
            
            client = self._get_client()
            response = client.send(message)
            
            return json.dumps({
                "success": True,
                "status_code": response.status_code,
                "message_id": response.headers.get('X-Message-Id'),
                "to": to_email,
                "template_id": template_id
            })
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
    
    def compose_progress_email(
        self,
        recipient_email: str,
        recipient_name: str,
        project_name: str,
        tasks_completed: int,
        tasks_in_progress: int,
        highlights: List[str],
        blockers: List[str],
        next_steps: List[str]
    ) -> str:
        """
        Compose and send a formatted progress report email.
        
        Args:
            recipient_email: Recipient email
            recipient_name: Recipient name
            project_name: Project name
            tasks_completed: Number of completed tasks
            tasks_in_progress: Number of in-progress tasks
            highlights: List of key achievements
            blockers: List of blockers
            next_steps: List of next steps
        
        Returns:
            JSON string with send status
        """
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #6366F1;">📊 {project_name} - Progress Report</h2>
            
            <div style="background: #f3f4f6; padding: 16px; border-radius: 8px; margin: 16px 0;">
                <h3 style="margin-top: 0;">Task Summary</h3>
                <p>✅ <strong>{tasks_completed}</strong> tasks completed</p>
                <p>🔄 <strong>{tasks_in_progress}</strong> tasks in progress</p>
            </div>
            
            <h3>🎉 Highlights</h3>
            <ul>
                {"".join(f"<li>{h}</li>" for h in highlights)}
            </ul>
            
            {"<h3>🚧 Blockers</h3><ul>" + "".join(f"<li>{b}</li>" for b in blockers) + "</ul>" if blockers else ""}
            
            <h3>📋 Next Steps</h3>
            <ul>
                {"".join(f"<li>{n}</li>" for n in next_steps)}
            </ul>
            
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
            <p style="color: #6b7280; font-size: 12px;">
                This report was automatically generated by Phonologic Operations
            </p>
        </body>
        </html>
        """
        
        subject = f"📊 {project_name} - Progress Report"
        
        return self.send_html_email(
            to_email=recipient_email,
            subject=subject,
            html_body=html_body,
            to_name=recipient_name
        )
