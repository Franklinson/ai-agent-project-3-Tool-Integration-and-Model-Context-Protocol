"""Communication tools for Email, Slack, and SMS with proper error handling."""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Any, Dict, List, Optional
import requests


class EmailTool:
    """Email tool using SMTP with error handling."""
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str, use_tls: bool = True):
        """Initialize email tool.
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            use_tls: Use TLS encryption
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        html: bool = False,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send email via SMTP.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            from_email: Sender email (defaults to username)
            cc: CC recipients
            bcc: BCC recipients
            html: Whether body is HTML
            attachments: List of file paths to attach
            
        Returns:
            Dictionary with success, message_id, and error
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email or self.username
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Attach body
            msg.attach(MIMEText(body, 'html' if html else 'plain'))
            
            # Attach files
            if attachments:
                for filepath in attachments:
                    try:
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition', f'attachment; filename={filepath.split("/")[-1]}')
                            msg.attach(part)
                    except Exception as e:
                        return {
                            "success": False,
                            "message_id": None,
                            "error": f"Failed to attach file {filepath}: {str(e)}"
                        }
            
            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                
                recipients = [to]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                
                server.sendmail(msg['From'], recipients, msg.as_string())
                
                return {
                    "success": True,
                    "message_id": msg['Message-ID'] if 'Message-ID' in msg else None,
                    "error": None
                }
        
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "message_id": None,
                "error": "SMTP authentication failed"
            }
        
        except smtplib.SMTPException as e:
            return {
                "success": False,
                "message_id": None,
                "error": f"SMTP error: {str(e)}"
            }
        
        except Exception as e:
            return {
                "success": False,
                "message_id": None,
                "error": f"Failed to send email: {str(e)}"
            }


class SlackTool:
    """Slack tool using webhooks with error handling."""
    
    def __init__(self, webhook_url: Optional[str] = None, bot_token: Optional[str] = None):
        """Initialize Slack tool.
        
        Args:
            webhook_url: Slack webhook URL
            bot_token: Slack bot token (for API)
        """
        self.webhook_url = webhook_url
        self.bot_token = bot_token
    
    def send_message(
        self,
        message: str,
        channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        blocks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Send message to Slack.
        
        Args:
            message: Message text
            channel: Channel name (required for API, optional for webhook)
            username: Bot username override
            icon_emoji: Bot icon emoji
            blocks: Slack blocks for rich formatting
            
        Returns:
            Dictionary with success, message_id, and error
        """
        try:
            if self.webhook_url:
                return self._send_webhook(message, username, icon_emoji, blocks)
            elif self.bot_token and channel:
                return self._send_api(message, channel, blocks)
            else:
                return {
                    "success": False,
                    "message_id": None,
                    "error": "No webhook URL or bot token configured"
                }
        
        except Exception as e:
            return {
                "success": False,
                "message_id": None,
                "error": f"Failed to send Slack message: {str(e)}"
            }
    
    def _send_webhook(
        self,
        message: str,
        username: Optional[str],
        icon_emoji: Optional[str],
        blocks: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Send message via webhook."""
        payload = {"text": message}
        
        if username:
            payload["username"] = username
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji
        if blocks:
            payload["blocks"] = blocks
        
        response = requests.post(
            self.webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200 and response.text == "ok":
            return {
                "success": True,
                "message_id": None,
                "error": None
            }
        else:
            return {
                "success": False,
                "message_id": None,
                "error": f"Slack webhook failed: {response.text}"
            }
    
    def _send_api(
        self,
        message: str,
        channel: str,
        blocks: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Send message via Slack API."""
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": channel,
            "text": message
        }
        
        if blocks:
            payload["blocks"] = blocks
        
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        data = response.json()
        
        if data.get("ok"):
            return {
                "success": True,
                "message_id": data.get("ts"),
                "error": None
            }
        else:
            return {
                "success": False,
                "message_id": None,
                "error": f"Slack API error: {data.get('error', 'Unknown error')}"
            }


class SMSTool:
    """SMS tool using Twilio with error handling."""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        """Initialize SMS tool.
        
        Args:
            account_sid: Twilio account SID
            auth_token: Twilio auth token
            from_number: Twilio phone number
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.api_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    
    def send_sms(
        self,
        to: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send SMS via Twilio.
        
        Args:
            to: Recipient phone number (E.164 format)
            message: Message text
            media_url: Optional media URL for MMS
            
        Returns:
            Dictionary with success, message_id, status, and error
        """
        try:
            payload = {
                "From": self.from_number,
                "To": to,
                "Body": message
            }
            
            if media_url:
                payload["MediaUrl"] = media_url
            
            response = requests.post(
                self.api_url,
                auth=(self.account_sid, self.auth_token),
                data=payload,
                timeout=10
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                return {
                    "success": True,
                    "message_id": data.get("sid"),
                    "status": data.get("status"),
                    "error": None
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "message_id": None,
                    "status": None,
                    "error": f"Twilio error: {error_data.get('message', response.text)}"
                }
        
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message_id": None,
                "status": None,
                "error": f"Request failed: {str(e)}"
            }
        
        except Exception as e:
            return {
                "success": False,
                "message_id": None,
                "status": None,
                "error": f"Failed to send SMS: {str(e)}"
            }


# Example usage and tests
if __name__ == "__main__":
    print("=== Communication Tools Demo ===\n")
    
    # Test 1: Email Tool (mock test)
    print("1. Email Tool Test:")
    print("Note: Configure with real SMTP credentials to test")
    print("Example usage:")
    print("""
    email_tool = EmailTool(
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        username="your-email@gmail.com",
        password="your-app-password"
    )
    
    result = email_tool.send_email(
        to="recipient@example.com",
        subject="Test Email",
        body="This is a test email",
        html=False
    )
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}")
    """)
    print()
    
    # Test 2: Slack Tool (webhook test with mock URL)
    print("2. Slack Tool Test:")
    print("Testing with invalid webhook (expected to fail):")
    slack_tool = SlackTool(webhook_url="https://hooks.slack.com/services/INVALID/WEBHOOK/URL")
    result = slack_tool.send_message(
        message="Test message",
        username="TestBot",
        icon_emoji=":robot_face:"
    )
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}")
    print()
    
    print("Example with real webhook:")
    print("""
    slack_tool = SlackTool(webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
    
    result = slack_tool.send_message(
        message="Hello from Python!",
        username="MyBot",
        icon_emoji=":robot_face:"
    )
    print(f"Success: {result['success']}")
    """)
    print()
    
    # Test 3: SMS Tool (mock test)
    print("3. SMS Tool Test:")
    print("Note: Configure with real Twilio credentials to test")
    print("Example usage:")
    print("""
    sms_tool = SMSTool(
        account_sid="your_account_sid",
        auth_token="your_auth_token",
        from_number="+1234567890"
    )
    
    result = sms_tool.send_sms(
        to="+1987654321",
        message="Hello from Python!"
    )
    print(f"Success: {result['success']}")
    print(f"Message ID: {result['message_id']}")
    print(f"Status: {result['status']}")
    """)
    print()
    
    # Test 4: Slack with blocks (rich formatting)
    print("4. Slack Rich Formatting Example:")
    print("""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Important Alert*\\nThis is a formatted message"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Acknowledge"},
                    "value": "ack"
                }
            ]
        }
    ]
    
    result = slack_tool.send_message(
        message="Fallback text",
        blocks=blocks
    )
    """)
    print()
    
    print("=== All tools support proper error handling ===")
    print("- Email: SMTP authentication, connection, and attachment errors")
    print("- Slack: Webhook/API failures, network errors")
    print("- SMS: Twilio API errors, invalid phone numbers, network errors")
