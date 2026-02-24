"""Comprehensive test suite for all tools with integration tests."""

import sys
import os
import tempfile
import shutil
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_tool import APIRequestTool, HTTPMethod
from communication_tool import EmailTool, SlackTool, SMSTool
from file_system_tool import FileSystemTool


class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def record_pass(self, test_name):
        self.passed += 1
        print(f"✓ {test_name}")
    
    def record_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"✗ {test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} passed")
        print(f"{'='*60}")
        if self.errors:
            print("\nFailed tests:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
        return self.failed == 0


results = TestResults()


def test_api_get_request():
    """Test HTTP GET request."""
    try:
        api_tool = APIRequestTool()
        result = api_tool.make_request(
            url="https://jsonplaceholder.typicode.com/posts/1",
            method=HTTPMethod.GET
        )
        assert result['success'], "GET request failed"
        assert result['status_code'] == 200, f"Expected 200, got {result['status_code']}"
        assert 'userId' in result['body'], "Response missing expected data"
        results.record_pass("API GET request")
    except Exception as e:
        results.record_fail("API GET request", str(e))


def test_api_post_request():
    """Test HTTP POST request with JSON."""
    try:
        api_tool = APIRequestTool()
        result = api_tool.make_request(
            url="https://jsonplaceholder.typicode.com/posts",
            method=HTTPMethod.POST,
            body={"title": "Test", "body": "Content", "userId": 1}
        )
        assert result['success'], "POST request failed"
        assert result['status_code'] == 201, f"Expected 201, got {result['status_code']}"
        results.record_pass("API POST request")
    except Exception as e:
        results.record_fail("API POST request", str(e))


def test_api_authentication():
    """Test API authentication headers."""
    try:
        api_tool = APIRequestTool()
        result = api_tool.make_request(
            url="https://httpbin.org/bearer",
            method=HTTPMethod.GET,
            auth_token="test-token"
        )
        assert result['success'], "Auth request failed"
        assert result['body']['authenticated'], "Token not authenticated"
        results.record_pass("API authentication")
    except Exception as e:
        results.record_fail("API authentication", str(e))


def test_api_timeout():
    """Test API timeout handling."""
    try:
        api_tool = APIRequestTool()
        result = api_tool.make_request(
            url="https://httpbin.org/delay/5",
            method=HTTPMethod.GET,
            timeout=1
        )
        assert not result['success'], "Should have timed out"
        assert "timeout" in result['error'].lower() or "timed out" in result['error'].lower(), "Expected timeout error"
        results.record_pass("API timeout handling")
    except Exception as e:
        results.record_fail("API timeout handling", str(e))


def test_api_http_error():
    """Test API HTTP error handling."""
    try:
        api_tool = APIRequestTool()
        result = api_tool.make_request(
            url="https://httpbin.org/status/404",
            method=HTTPMethod.GET
        )
        assert not result['success'], "Should have failed with 404"
        assert result['status_code'] == 404, f"Expected 404, got {result['status_code']}"
        results.record_pass("API HTTP error handling")
    except Exception as e:
        results.record_fail("API HTTP error handling", str(e))


def test_api_rate_limiting():
    """Test API rate limiting."""
    try:
        import time
        api_tool = APIRequestTool(rate_limit_delay=0.5)
        
        start = time.time()
        api_tool.make_request(url="https://httpbin.org/get", method=HTTPMethod.GET)
        api_tool.make_request(url="https://httpbin.org/get", method=HTTPMethod.GET)
        elapsed = time.time() - start
        
        assert elapsed >= 0.5, f"Rate limit not applied: {elapsed}s"
        results.record_pass("API rate limiting")
    except Exception as e:
        results.record_fail("API rate limiting", str(e))


def test_slack_webhook_validation():
    """Test Slack webhook validation."""
    try:
        slack_tool = SlackTool(webhook_url="https://hooks.slack.com/invalid")
        result = slack_tool.send_message("Test message")
        assert not result['success'], "Should fail with invalid webhook"
        assert result['error'] is not None, "Should have error message"
        results.record_pass("Slack webhook validation")
    except Exception as e:
        results.record_fail("Slack webhook validation", str(e))


def test_slack_no_config():
    """Test Slack with no configuration."""
    try:
        slack_tool = SlackTool()
        result = slack_tool.send_message("Test")
        assert not result['success'], "Should fail with no config"
        assert "No webhook URL or bot token" in result['error'], "Wrong error message"
        results.record_pass("Slack no config error")
    except Exception as e:
        results.record_fail("Slack no config error", str(e))


def test_email_invalid_smtp():
    """Test Email with invalid SMTP server."""
    try:
        email_tool = EmailTool(
            smtp_host="invalid.smtp.server",
            smtp_port=587,
            username="test@test.com",
            password="password"
        )
        result = email_tool.send_email(
            to="recipient@test.com",
            subject="Test",
            body="Test"
        )
        assert not result['success'], "Should fail with invalid SMTP"
        results.record_pass("Email invalid SMTP")
    except Exception as e:
        results.record_fail("Email invalid SMTP", str(e))


def test_sms_invalid_credentials():
    """Test SMS with invalid credentials."""
    try:
        sms_tool = SMSTool(
            account_sid="invalid_sid",
            auth_token="invalid_token",
            from_number="+1234567890"
        )
        result = sms_tool.send_sms(to="+1987654321", message="Test")
        assert not result['success'], "Should fail with invalid credentials"
        results.record_pass("SMS invalid credentials")
    except Exception as e:
        results.record_fail("SMS invalid credentials", str(e))


def test_fs_read_write():
    """Test file system read and write."""
    sandbox = tempfile.mkdtemp(prefix="test_fs_")
    try:
        fs_tool = FileSystemTool(sandbox_dir=sandbox)
        
        # Write file
        write_result = fs_tool.write_file("test.txt", "Hello, World!")
        assert write_result['success'], "Write failed"
        assert write_result['bytes_written'] == 13, "Wrong byte count"
        
        # Read file
        read_result = fs_tool.read_file("test.txt")
        assert read_result['success'], "Read failed"
        assert read_result['content'] == "Hello, World!", "Content mismatch"
        
        results.record_pass("FS read/write")
    except Exception as e:
        results.record_fail("FS read/write", str(e))
    finally:
        shutil.rmtree(sandbox)


def test_fs_list_directory():
    """Test file system directory listing."""
    sandbox = tempfile.mkdtemp(prefix="test_fs_")
    try:
        fs_tool = FileSystemTool(sandbox_dir=sandbox)
        
        fs_tool.write_file("file1.txt", "content1")
        fs_tool.write_file("file2.txt", "content2")
        fs_tool.write_file("subdir/file3.txt", "content3")
        
        result = fs_tool.list_directory(".")
        assert result['success'], "List failed"
        assert len(result['files']) == 2, f"Expected 2 files, got {len(result['files'])}"
        assert len(result['directories']) == 1, f"Expected 1 dir, got {len(result['directories'])}"
        
        results.record_pass("FS list directory")
    except Exception as e:
        results.record_fail("FS list directory", str(e))
    finally:
        shutil.rmtree(sandbox)


def test_fs_delete_file():
    """Test file system delete."""
    sandbox = tempfile.mkdtemp(prefix="test_fs_")
    try:
        fs_tool = FileSystemTool(sandbox_dir=sandbox)
        
        fs_tool.write_file("delete_me.txt", "content")
        delete_result = fs_tool.delete_file("delete_me.txt")
        assert delete_result['success'], "Delete failed"
        
        read_result = fs_tool.read_file("delete_me.txt")
        assert not read_result['success'], "File should not exist"
        
        results.record_pass("FS delete file")
    except Exception as e:
        results.record_fail("FS delete file", str(e))
    finally:
        shutil.rmtree(sandbox)


def test_fs_path_traversal():
    """Test file system path traversal prevention."""
    sandbox = tempfile.mkdtemp(prefix="test_fs_")
    try:
        fs_tool = FileSystemTool(sandbox_dir=sandbox)
        
        attacks = [
            "../../../etc/passwd",
            "../../etc/passwd",
            "subdir/../../etc/passwd"
        ]
        
        for attack in attacks:
            result = fs_tool.read_file(attack)
            assert not result['success'], f"Path traversal not blocked: {attack}"
            assert "outside sandbox" in result['error'], "Wrong error message"
        
        results.record_pass("FS path traversal prevention")
    except Exception as e:
        results.record_fail("FS path traversal prevention", str(e))
    finally:
        shutil.rmtree(sandbox)


def test_fs_absolute_path():
    """Test file system absolute path blocking."""
    sandbox = tempfile.mkdtemp(prefix="test_fs_")
    try:
        fs_tool = FileSystemTool(sandbox_dir=sandbox)
        
        attacks = ["/etc/passwd", "/tmp/malicious.txt"]
        
        for attack in attacks:
            result = fs_tool.read_file(attack)
            assert not result['success'], f"Absolute path not blocked: {attack}"
            assert "outside sandbox" in result['error'], "Wrong error message"
        
        results.record_pass("FS absolute path blocking")
    except Exception as e:
        results.record_fail("FS absolute path blocking", str(e))
    finally:
        shutil.rmtree(sandbox)


def test_fs_file_type_whitelist():
    """Test file system file type restrictions."""
    sandbox = tempfile.mkdtemp(prefix="test_fs_")
    try:
        fs_tool = FileSystemTool(
            sandbox_dir=sandbox,
            allowed_extensions={'.txt', '.json'}
        )
        
        # Allowed
        result = fs_tool.write_file("allowed.txt", "content")
        assert result['success'], "Allowed file type blocked"
        
        # Disallowed
        result = fs_tool.write_file("blocked.exe", "content")
        assert not result['success'], "Disallowed file type not blocked"
        assert "not allowed" in result['error'], "Wrong error message"
        
        results.record_pass("FS file type whitelist")
    except Exception as e:
        results.record_fail("FS file type whitelist", str(e))
    finally:
        shutil.rmtree(sandbox)


def test_fs_file_size_limit():
    """Test file system file size limits."""
    sandbox = tempfile.mkdtemp(prefix="test_fs_")
    try:
        fs_tool = FileSystemTool(sandbox_dir=sandbox, max_file_size=1024)
        
        # Small file
        result = fs_tool.write_file("small.txt", "x" * 500)
        assert result['success'], "Small file blocked"
        
        # Large file
        result = fs_tool.write_file("large.txt", "x" * 2048)
        assert not result['success'], "Large file not blocked"
        assert "exceeds maximum" in result['error'], "Wrong error message"
        
        results.record_pass("FS file size limit")
    except Exception as e:
        results.record_fail("FS file size limit", str(e))
    finally:
        shutil.rmtree(sandbox)


def test_integration_api_to_file():
    """Integration: Fetch API data and save to file."""
    sandbox = tempfile.mkdtemp(prefix="test_integration_")
    try:
        # Fetch data from API
        api_tool = APIRequestTool()
        api_result = api_tool.make_request(
            url="https://jsonplaceholder.typicode.com/posts/1",
            method=HTTPMethod.GET
        )
        assert api_result['success'], "API request failed"
        
        # Save to file
        fs_tool = FileSystemTool(sandbox_dir=sandbox)
        data = json.dumps(api_result['body'], indent=2)
        write_result = fs_tool.write_file("api_data.json", data)
        assert write_result['success'], "File write failed"
        
        # Read back and verify
        read_result = fs_tool.read_file("api_data.json")
        assert read_result['success'], "File read failed"
        saved_data = json.loads(read_result['content'])
        assert saved_data['userId'] == api_result['body']['userId'], "Data mismatch"
        
        results.record_pass("Integration: API to File")
    except Exception as e:
        results.record_fail("Integration: API to File", str(e))
    finally:
        shutil.rmtree(sandbox)


def test_integration_file_to_api():
    """Integration: Read file and POST to API."""
    sandbox = tempfile.mkdtemp(prefix="test_integration_")
    try:
        # Create file with data
        fs_tool = FileSystemTool(sandbox_dir=sandbox)
        data = {"title": "Test Post", "body": "Test content", "userId": 1}
        fs_tool.write_file("post_data.json", json.dumps(data))
        
        # Read file
        read_result = fs_tool.read_file("post_data.json")
        assert read_result['success'], "File read failed"
        post_data = json.loads(read_result['content'])
        
        # POST to API
        api_tool = APIRequestTool()
        api_result = api_tool.make_request(
            url="https://jsonplaceholder.typicode.com/posts",
            method=HTTPMethod.POST,
            body=post_data
        )
        assert api_result['success'], "API POST failed"
        assert api_result['status_code'] == 201, "Wrong status code"
        
        results.record_pass("Integration: File to API")
    except Exception as e:
        results.record_fail("Integration: File to API", str(e))
    finally:
        shutil.rmtree(sandbox)


def test_integration_api_error_notification():
    """Integration: API error triggers notification attempt."""
    try:
        # Make failing API request
        api_tool = APIRequestTool()
        api_result = api_tool.make_request(
            url="https://httpbin.org/status/500",
            method=HTTPMethod.GET
        )
        assert not api_result['success'], "API should have failed"
        
        # Attempt to send notification (will fail but tests integration)
        slack_tool = SlackTool(webhook_url="https://hooks.slack.com/invalid")
        notification = slack_tool.send_message(
            f"API Error: {api_result['error']}"
        )
        # We expect this to fail, but it demonstrates the integration
        assert not notification['success'], "Notification should fail (expected)"
        
        results.record_pass("Integration: API error notification")
    except Exception as e:
        results.record_fail("Integration: API error notification", str(e))


def test_integration_log_to_file():
    """Integration: Log API responses to file."""
    sandbox = tempfile.mkdtemp(prefix="test_integration_")
    try:
        fs_tool = FileSystemTool(sandbox_dir=sandbox)
        api_tool = APIRequestTool()
        
        # Make multiple API requests and log
        log_entries = []
        for i in range(1, 4):
            result = api_tool.make_request(
                url=f"https://jsonplaceholder.typicode.com/posts/{i}",
                method=HTTPMethod.GET
            )
            log_entries.append({
                "id": i,
                "success": result['success'],
                "status": result['status_code']
            })
        
        # Write log file
        log_content = json.dumps(log_entries, indent=2)
        write_result = fs_tool.write_file("api_log.json", log_content)
        assert write_result['success'], "Log write failed"
        
        # Verify log
        read_result = fs_tool.read_file("api_log.json")
        assert read_result['success'], "Log read failed"
        logs = json.loads(read_result['content'])
        assert len(logs) == 3, f"Expected 3 log entries, got {len(logs)}"
        
        results.record_pass("Integration: Log to file")
    except Exception as e:
        results.record_fail("Integration: Log to file", str(e))
    finally:
        shutil.rmtree(sandbox)


def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("COMPREHENSIVE TOOL TEST SUITE")
    print("="*60)
    
    print("\n--- HTTP API Tool Tests ---")
    test_api_get_request()
    test_api_post_request()
    test_api_authentication()
    test_api_timeout()
    test_api_http_error()
    test_api_rate_limiting()
    
    print("\n--- Communication Tool Tests ---")
    test_slack_webhook_validation()
    test_slack_no_config()
    test_email_invalid_smtp()
    test_sms_invalid_credentials()
    
    print("\n--- File System Tool Tests ---")
    test_fs_read_write()
    test_fs_list_directory()
    test_fs_delete_file()
    
    print("\n--- Security Tests ---")
    test_fs_path_traversal()
    test_fs_absolute_path()
    test_fs_file_type_whitelist()
    test_fs_file_size_limit()
    
    print("\n--- Integration Tests ---")
    test_integration_api_to_file()
    test_integration_file_to_api()
    test_integration_api_error_notification()
    test_integration_log_to_file()
    
    return results.summary()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
