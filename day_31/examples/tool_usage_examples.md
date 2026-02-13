# Tool Usage Examples

Comprehensive examples for all tools including basic usage, advanced scenarios, error handling, and best practices.

---

## web_search

### Basic Usage Example

```python
# Simple web search with default settings
result = web_search(
    query="Python asyncio tutorial"
)

# Returns up to 5 results by default
for item in result:
    print(f"{item['title']}: {item['url']}")
```

### Advanced Use Case

```python
# Multi-language search with custom result limit
result = web_search(
    query="recetas de paella valenciana",
    num_results=10,
    language="es"
)

# Process results with filtering
relevant_results = [
    r for r in result 
    if "tradicional" in r['snippet'].lower()
]

# Batch multiple searches efficiently
queries = ["Python best practices", "JavaScript frameworks", "Go concurrency"]
results = {}

for query in queries:
    try:
        results[query] = web_search(query=query, num_results=3)
    except RateLimitError:
        # Implement exponential backoff
        time.sleep(2)
        results[query] = web_search(query=query, num_results=3)
```

### Error Handling Example

```python
import time

def safe_web_search(query, max_retries=3):
    """Web search with comprehensive error handling."""
    
    # Validate query length
    if len(query) > 500:
        raise ValueError("Query exceeds 500 character limit")
    
    if not query.strip():
        raise ValueError("Query cannot be empty")
    
    for attempt in range(max_retries):
        try:
            result = web_search(query=query, num_results=5)
            
            # Handle empty results
            if not result:
                print(f"No results found for: {query}")
                return []
            
            return result
            
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limit hit. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Try again later.")
                raise
                
        except NetworkError as e:
            print(f"Network error: {e}. Retrying...")
            time.sleep(1)
            
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    return []
```

### Common Mistakes to Avoid

❌ **Don't**: Make rapid successive calls without rate limiting
```python
# BAD: Will hit rate limits
for query in large_query_list:
    web_search(query=query)  # Too fast!
```

✓ **Do**: Implement rate limiting and batching
```python
# GOOD: Respect rate limits
for query in large_query_list:
    result = web_search(query=query)
    time.sleep(0.5)  # Throttle requests
```

❌ **Don't**: Ignore empty or invalid queries
```python
# BAD: No validation
web_search(query="")  # Will fail
```

✓ **Do**: Validate input before calling
```python
# GOOD: Validate first
if query and len(query) <= 500:
    web_search(query=query)
```

### Best Practices

1. **Cache results** to avoid redundant searches
2. **Implement retry logic** with exponential backoff
3. **Validate queries** before making API calls
4. **Monitor rate limits** and adjust request frequency
5. **Use specific queries** for better results
6. **Set appropriate num_results** based on needs (lower = faster)

---

## query_database

### Basic Usage Example

```python
# Simple SELECT query with parameters
result = query_database(
    query="SELECT * FROM users WHERE active = ?",
    database="production",
    parameters=[True]
)

# Access results
for row in result['rows']:
    print(f"User: {row['name']}, Email: {row['email']}")

print(f"Total rows: {result['rowCount']}")
```

### Advanced Use Case

```python
# Complex JOIN query with multiple parameters
query = """
    SELECT 
        u.id, u.name, u.email,
        COUNT(o.id) as order_count,
        SUM(o.total) as total_spent
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.created_at > ? 
        AND u.status = ?
    GROUP BY u.id, u.name, u.email
    HAVING COUNT(o.id) > ?
    ORDER BY total_spent DESC
"""

result = query_database(
    query=query,
    database="analytics",
    parameters=["2024-01-01", "active", 5],
    timeout=15,
    max_rows=1000
)

# Process aggregated results
top_customers = result['rows'][:10]
for customer in top_customers:
    print(f"{customer['name']}: {customer['order_count']} orders, "
          f"${customer['total_spent']:.2f}")

# Pagination for large datasets
def paginated_query(base_query, database, page_size=100):
    """Execute query with pagination."""
    offset = 0
    while True:
        paginated = f"{base_query} LIMIT ? OFFSET ?"
        result = query_database(
            query=paginated,
            database=database,
            parameters=[page_size, offset]
        )
        
        if not result['rows']:
            break
            
        yield result['rows']
        offset += page_size
```

### Error Handling Example

```python
def safe_database_query(query, database, parameters=None):
    """Database query with comprehensive error handling."""
    
    # Validate query is SELECT only
    if not query.strip().upper().startswith('SELECT'):
        raise ValueError("Only SELECT queries are allowed")
    
    # Check for dangerous keywords
    dangerous = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'TRUNCATE']
    query_upper = query.upper()
    if any(keyword in query_upper for keyword in dangerous):
        raise ValueError("Query contains disallowed operations")
    
    try:
        result = query_database(
            query=query,
            database=database,
            parameters=parameters or [],
            timeout=30
        )
        
        # Validate result structure
        if 'rows' not in result:
            raise ValueError("Invalid result format")
        
        return result
        
    except TimeoutError:
        print("Query exceeded timeout. Consider optimizing or adding indexes.")
        raise
        
    except DatabaseNotFoundError:
        print(f"Database '{database}' not found. Check configuration.")
        raise
        
    except PermissionError:
        print("Insufficient permissions. Contact administrator.")
        raise
        
    except SyntaxError as e:
        print(f"SQL syntax error: {e}")
        print("Check query syntax and parameter placeholders.")
        raise
        
    except Exception as e:
        print(f"Database error: {e}")
        raise
```

### Common Mistakes to Avoid

❌ **Don't**: Concatenate user input into queries
```python
# BAD: SQL injection risk!
user_input = "admin' OR '1'='1"
query = f"SELECT * FROM users WHERE name = '{user_input}'"
query_database(query=query, database="prod")
```

✓ **Do**: Always use parameterized queries
```python
# GOOD: Safe parameterization
query = "SELECT * FROM users WHERE name = ?"
query_database(query=query, database="prod", parameters=[user_input])
```

❌ **Don't**: Fetch unlimited rows
```python
# BAD: May cause memory issues
query_database(query="SELECT * FROM huge_table", database="prod")
```

✓ **Do**: Use LIMIT and max_rows
```python
# GOOD: Limit result set
query_database(
    query="SELECT * FROM huge_table LIMIT ?",
    database="prod",
    parameters=[1000],
    max_rows=1000
)
```

### Best Practices

1. **Always use parameterized queries** - Never concatenate user input
2. **Set appropriate timeouts** - Prevent long-running queries
3. **Use LIMIT clauses** - Control result set size
4. **Add proper indexes** - Optimize query performance
5. **Test queries** on development database first
6. **Monitor query performance** - Log slow queries
7. **Use connection pooling** - Reuse database connections

---

## send_email

### Basic Usage Example

```python
# Simple plain text email
result = send_email(
    to=["user@example.com"],
    subject="Welcome to Our Service",
    body="Thank you for signing up! We're excited to have you."
)

print(f"Email sent: {result['message_id']}")
print(f"Status: {result['status']}")
```

### Advanced Use Case

```python
# HTML email with multiple recipients and priority
html_content = """
<html>
<body>
    <h1>Weekly Report</h1>
    <p>Here's your weekly summary:</p>
    <ul>
        <li>New users: 150</li>
        <li>Revenue: $12,500</li>
        <li>Active sessions: 1,200</li>
    </ul>
    <p>Best regards,<br>The Team</p>
</body>
</html>
"""

result = send_email(
    to=["team@example.com", "manager@example.com"],
    cc=["stakeholder@example.com"],
    bcc=["archive@example.com"],
    subject="Weekly Report - Week 3",
    body=html_content,
    html=True,
    priority="high"
)

# Batch email sending with rate limiting
def send_bulk_emails(recipients, subject, body, batch_size=10):
    """Send emails in batches to respect rate limits."""
    results = []
    
    for i in range(0, len(recipients), batch_size):
        batch = recipients[i:i + batch_size]
        
        try:
            result = send_email(
                to=batch,
                subject=subject,
                body=body
            )
            results.append(result)
            
            # Wait between batches
            if i + batch_size < len(recipients):
                time.sleep(2)
                
        except RateLimitError as e:
            print(f"Rate limit hit at batch {i//batch_size + 1}")
            time.sleep(60)  # Wait 1 minute
            # Retry batch
            result = send_email(to=batch, subject=subject, body=body)
            results.append(result)
    
    return results
```

### Error Handling Example

```python
import re

def safe_send_email(to, subject, body, **kwargs):
    """Send email with comprehensive validation and error handling."""
    
    # Validate email addresses
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    invalid_emails = [
        email for email in to 
        if not re.match(email_pattern, email)
    ]
    
    if invalid_emails:
        raise ValueError(f"Invalid email addresses: {invalid_emails}")
    
    # Validate subject and body
    if not subject or len(subject) > 200:
        raise ValueError("Subject must be 1-200 characters")
    
    if not body or len(body) > 100000:
        raise ValueError("Body must be 1-100,000 characters")
    
    # Check recipient limits
    total_recipients = len(to) + len(kwargs.get('cc', [])) + len(kwargs.get('bcc', []))
    if total_recipients > 70:
        raise ValueError("Total recipients exceed limit of 70")
    
    try:
        result = send_email(
            to=to,
            subject=subject,
            body=body,
            **kwargs
        )
        
        return result
        
    except RateLimitError as e:
        print(f"Rate limit exceeded. Retry after: {e.retry_after}")
        raise
        
    except SMTPConnectionError:
        print("Failed to connect to mail server. Check network.")
        raise
        
    except AuthenticationError:
        print("SMTP authentication failed. Check credentials.")
        raise
        
    except RecipientRejectedError as e:
        print(f"Recipients rejected: {e.rejected_recipients}")
        # Retry with valid recipients only
        valid_recipients = [r for r in to if r not in e.rejected_recipients]
        if valid_recipients:
            return send_email(to=valid_recipients, subject=subject, body=body)
        raise
        
    except MessageTooLargeError:
        print("Email exceeds size limit. Remove attachments or reduce content.")
        raise
        
    except SpamDetectedError as e:
        print(f"Content flagged as spam: {e.suggestions}")
        raise
```

### Common Mistakes to Avoid

❌ **Don't**: Send to unvalidated email addresses
```python
# BAD: No validation
send_email(to=["invalid-email"], subject="Test", body="Test")
```

✓ **Do**: Validate emails before sending
```python
# GOOD: Validate first
if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
    send_email(to=[email], subject="Test", body="Test")
```

❌ **Don't**: Ignore rate limits
```python
# BAD: Will hit rate limits
for user in users:
    send_email(to=[user.email], subject="News", body="...")
```

✓ **Do**: Batch and throttle requests
```python
# GOOD: Respect rate limits
for i in range(0, len(users), 10):
    batch = users[i:i+10]
    send_email(to=[u.email for u in batch], subject="News", body="...")
    time.sleep(2)
```

❌ **Don't**: Send large attachments without checking
```python
# BAD: May exceed size limit
send_email(to=["user@example.com"], subject="File", 
           body="See attachment", attachments=["huge_file.zip"])
```

✓ **Do**: Check size limits and compress if needed
```python
# GOOD: Validate size
if file_size < 20_000_000:  # 20MB
    send_email(to=["user@example.com"], subject="File", 
               body="See attachment", attachments=["file.zip"])
```

### Best Practices

1. **Validate all email addresses** before sending
2. **Use HTML sparingly** - Provide plain text alternative
3. **Respect rate limits** - Batch emails and add delays
4. **Monitor bounce rates** - Remove invalid addresses
5. **Include unsubscribe links** - Follow email best practices
6. **Test emails** in development environment first
7. **Log all sends** - Track delivery status
8. **Handle errors gracefully** - Retry with exponential backoff
9. **Keep subject lines clear** - Avoid spam trigger words
10. **Personalize content** - Use recipient names when possible

---

## General Best Practices

### Error Handling Pattern

```python
def execute_tool_safely(tool_func, *args, **kwargs):
    """Generic error handling wrapper for all tools."""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            return tool_func(*args, **kwargs)
            
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                time.sleep(wait)
            else:
                raise
                
        except NetworkError:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise
                
        except Exception as e:
            print(f"Tool execution failed: {e}")
            raise
```

### Logging Pattern

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def logged_tool_call(tool_name, **params):
    """Log tool calls for monitoring."""
    logger.info(f"Calling {tool_name} with params: {params}")
    
    try:
        result = globals()[tool_name](**params)
        logger.info(f"{tool_name} succeeded")
        return result
    except Exception as e:
        logger.error(f"{tool_name} failed: {e}")
        raise
```

### Testing Pattern

```python
def test_tool_with_mock_data():
    """Test tools with safe mock data."""
    # Use test database
    result = query_database(
        query="SELECT * FROM test_users LIMIT ?",
        database="test_db",
        parameters=[5]
    )
    
    # Use test email
    result = send_email(
        to=["test@example.com"],
        subject="Test Email",
        body="This is a test"
    )
    
    assert result['status'] == 'sent'
```
