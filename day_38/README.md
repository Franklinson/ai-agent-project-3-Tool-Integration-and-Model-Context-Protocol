# Communication Tools

Comprehensive communication tools for Email (SMTP), Slack (Webhook/API), and SMS (Twilio) with proper error handling and delivery status.

## Features

### Email Tool (SMTP)
- Send emails via SMTP
- Support for HTML and plain text
- CC and BCC recipients
- File attachments
- Comprehensive error handling

### Slack Tool
- Webhook and API support
- Rich message formatting with blocks
- Custom username and emoji
- Channel targeting (API mode)

### SMS Tool (Twilio)
- Send SMS messages
- MMS support with media URLs
- Delivery status tracking
- E.164 phone number format

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Email Tool

```python
from communication_tool import EmailTool

# Initialize
email_tool = EmailTool(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    username="your-email@gmail.com",
    password="your-app-password"
)

# Send email
result = email_tool.send_email(
    to="recipient@example.com",
    subject="Test Email",
    body="This is a test email",
    html=False,
    attachments=["/path/to/file.pdf"]
)

print(f"Success: {result['success']}")
print(f"Error: {result['error']}")
```

### Slack Tool (Webhook)

```python
from communication_tool import SlackTool

# Initialize with webhook
slack_tool = SlackTool(
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
)

# Send simple message
result = slack_tool.send_message(
    message="Hello from Python!",
    username="MyBot",
    icon_emoji=":robot_face:"
)

# Send with rich formatting
blocks = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Important Alert*\nThis is a formatted message"
        }
    }
]

result = slack_tool.send_message(
    message="Fallback text",
    blocks=blocks
)
```

### Slack Tool (API)

```python
# Initialize with bot token
slack_tool = SlackTool(bot_token="xoxb-your-bot-token")

# Send to specific channel
result = slack_tool.send_message(
    message="Hello!",
    channel="#general"
)

print(f"Message ID: {result['message_id']}")
```

### SMS Tool

```python
from communication_tool import SMSTool

# Initialize
sms_tool = SMSTool(
    account_sid="your_account_sid",
    auth_token="your_auth_token",
    from_number="+1234567890"
)

# Send SMS
result = sms_tool.send_sms(
    to="+1987654321",
    message="Hello from Python!"
)

print(f"Success: {result['success']}")
print(f"Message ID: {result['message_id']}")
print(f"Status: {result['status']}")
```

## Output Schema

All tools return a dictionary with the following structure:

```python
{
    "success": bool,        # Whether the operation succeeded
    "message_id": str,      # Message ID (if available)
    "error": str,           # Error message (if failed)
    "status": str           # Delivery status (SMS only)
}
```

## Error Handling

All tools include comprehensive error handling for:

- **Email**: SMTP authentication errors, connection errors, attachment errors
- **Slack**: Webhook failures, API errors, network errors
- **SMS**: Twilio API errors, invalid phone numbers, network errors

## Configuration

### Gmail SMTP Setup
1. Enable 2-factor authentication
2. Generate an app password
3. Use `smtp.gmail.com` with port 587

### Slack Webhook Setup
1. Go to your Slack workspace settings
2. Create an Incoming Webhook
3. Copy the webhook URL

### Twilio Setup
1. Sign up for Twilio account
2. Get Account SID and Auth Token
3. Purchase a phone number

## Testing

Run the test suite:

```bash
python test_communication.py
```

## Requirements

- Python 3.7+
- requests library (for Slack and SMS)
- Built-in smtplib (for Email)
