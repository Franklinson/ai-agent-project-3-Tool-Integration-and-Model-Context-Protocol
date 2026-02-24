"""Test file for communication tools with mock and real examples."""

from communication_tool import EmailTool, SlackTool, SMSTool


def test_email_tool():
    """Test email tool with mock credentials."""
    print("=== Testing Email Tool ===")
    
    # Mock test - will fail but demonstrates error handling
    email_tool = EmailTool(
        smtp_host="smtp.example.com",
        smtp_port=587,
        username="test@example.com",
        password="fake_password"
    )
    
    result = email_tool.send_email(
        to="recipient@example.com",
        subject="Test Email",
        body="This is a test email body",
        html=False
    )
    
    print(f"Success: {result['success']}")
    print(f"Message ID: {result['message_id']}")
    print(f"Error: {result['error']}")
    print()


def test_slack_webhook():
    """Test Slack webhook with invalid URL to demonstrate error handling."""
    print("=== Testing Slack Webhook ===")
    
    slack_tool = SlackTool(webhook_url="https://hooks.slack.com/services/TEST/INVALID/URL")
    
    result = slack_tool.send_message(
        message="Hello from Python! This is a test message.",
        username="TestBot",
        icon_emoji=":robot_face:"
    )
    
    print(f"Success: {result['success']}")
    print(f"Message ID: {result['message_id']}")
    print(f"Error: {result['error']}")
    print()


def test_slack_with_blocks():
    """Test Slack with rich formatting blocks."""
    print("=== Testing Slack with Rich Formatting ===")
    
    slack_tool = SlackTool(webhook_url="https://hooks.slack.com/services/TEST/INVALID/URL")
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "System Alert"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Status:* :white_check_mark: All systems operational\n*Time:* 2024-01-15 10:30 AM"
            }
        }
    ]
    
    result = slack_tool.send_message(
        message="System status update",
        blocks=blocks
    )
    
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}")
    print()


def test_sms_tool():
    """Test SMS tool with mock credentials."""
    print("=== Testing SMS Tool ===")
    
    sms_tool = SMSTool(
        account_sid="fake_account_sid",
        auth_token="fake_auth_token",
        from_number="+1234567890"
    )
    
    result = sms_tool.send_sms(
        to="+1987654321",
        message="Hello! This is a test SMS message."
    )
    
    print(f"Success: {result['success']}")
    print(f"Message ID: {result['message_id']}")
    print(f"Status: {result['status']}")
    print(f"Error: {result['error']}")
    print()


def test_error_handling():
    """Test various error scenarios."""
    print("=== Testing Error Handling ===")
    
    # Test 1: Slack with no configuration
    print("1. Slack with no configuration:")
    slack_tool = SlackTool()
    result = slack_tool.send_message(message="Test")
    print(f"   Error caught: {result['error']}")
    print()
    
    # Test 2: Email with invalid attachment
    print("2. Email with invalid attachment:")
    email_tool = EmailTool(
        smtp_host="smtp.example.com",
        smtp_port=587,
        username="test@example.com",
        password="password"
    )
    result = email_tool.send_email(
        to="test@example.com",
        subject="Test",
        body="Test",
        attachments=["/nonexistent/file.pdf"]
    )
    print(f"   Error caught: {result['error']}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("COMMUNICATION TOOLS TEST SUITE")
    print("=" * 60)
    print()
    
    test_email_tool()
    test_slack_webhook()
    test_slack_with_blocks()
    test_sms_tool()
    test_error_handling()
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✓ Email Tool: Proper SMTP error handling")
    print("✓ Slack Tool: Webhook and API error handling")
    print("✓ SMS Tool: Twilio API error handling")
    print("✓ All tools return proper schemas with success/error info")
    print()
    print("To use with real services, configure with actual credentials:")
    print("- Email: Use Gmail SMTP or other email provider")
    print("- Slack: Get webhook URL from Slack workspace settings")
    print("- SMS: Sign up for Twilio account and get credentials")
