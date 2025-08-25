# URL Validator Documentation

## Overview

The URL Validator is an automatic validation system for LLM-generated datasource links in DataScope AI. It validates URLs, eliminates 404s, follows redirections, and reports errors as requested in issue #66.

## Features

### Core Validation Capabilities
- **URL Format Validation**: Checks if URLs have valid format (http/https with domain)
- **HTTP Status Checking**: Detects 404 Not Found, server errors (5xx), and accessibility issues
- **Redirect Following**: Automatically follows redirects and updates to final URL
- **Connection Error Handling**: Handles timeouts, DNS failures, and connection errors
- **User-Agent Setting**: Uses appropriate User-Agent to avoid blocking

### Integration Points
- **Automatic Validation**: All LLM-generated URLs are validated during pipeline processing
- **Non-blocking**: Failed URLs are marked but not removed (allows manual review)
- **Metadata Enrichment**: Adds validation status and error details to dataset suggestions

## Architecture

### Core Components

#### 1. ValidationStatus Enum
```python
class ValidationStatus(Enum):
    VALID = "valid"              # URL is accessible (HTTP 200, 2xx, 3xx, 4xx except 404)
    NOT_FOUND = "404"            # URL returns 404 Not Found
    REDIRECTED = "redirected"    # URL redirected to different location
    TIMEOUT = "timeout"          # Request timeout
    CONNECTION_ERROR = "connection_error"  # DNS, network, or other connection issues
    INVALID_URL = "invalid_url"  # Invalid URL format
    SERVER_ERROR = "server_error"  # Server error (5xx)
```

#### 2. ValidationResult Dataclass
```python
@dataclass
class ValidationResult:
    status: ValidationStatus
    final_url: Optional[str] = None      # Final URL after redirects
    error_message: Optional[str] = None   # Error description
    status_code: Optional[int] = None     # HTTP status code
    redirected_from: Optional[str] = None # Original URL if redirected
```

#### 3. URLValidator Class
Main validation engine with configurable timeout and redirect limits.

### Schema Integration

Added new fields to `DatasetSuggestion`:
```python
class DatasetSuggestion(BaseModel):
    # ... existing fields ...
    url_validation_status: str | None = None  # Validation status
    url_validation_error: str | None = None   # Error message if any
    final_url: str | None = None              # Final URL after redirects
```

### Pipeline Integration

Modified `_llm_to_ds()` function in `ai_engine/pipeline.py`:
```python
def _llm_to_ds(item: LLMSourceSuggestion, *, angle_idx: int) -> DatasetSuggestion:
    # Validate URL before creating DatasetSuggestion
    validation_result = validate_url(item.link)
    
    # Use final URL after redirects
    final_url = validation_result.final_url or item.link
    
    return DatasetSuggestion(
        # ... other fields ...
        source_url=final_url,
        url_validation_status=validation_result.status.value,
        url_validation_error=validation_result.error_message,
        final_url=final_url if validation_result.final_url != item.link else None,
    )
```

## Usage Examples

### Standalone Usage
```python
from ai_engine.url_validator import URLValidator, validate_url

# Using the class
validator = URLValidator(timeout=10)
result = validator.validate_url("https://example.com/dataset")

print(f"Status: {result.status.value}")
print(f"Final URL: {result.final_url}")
if result.error_message:
    print(f"Error: {result.error_message}")

# Using convenience function
result = validate_url("https://example.com/dataset")
```

### Bulk Validation
```python
validator = URLValidator()
urls = ["https://site1.com", "https://site2.com", "invalid-url"]
results = validator.validate_urls(urls)

for url, result in results.items():
    print(f"{url}: {result.status.value}")
```

### Accessibility Check
```python
from ai_engine.url_validator import is_url_accessible

if is_url_accessible("https://example.com/dataset"):
    print("URL is accessible")
else:
    print("URL is not accessible")
```

## Validation Logic

### 1. Format Validation
- Checks if URL string is not empty
- Validates URL has http/https scheme
- Ensures URL has a valid domain

### 2. HTTP Validation
- Sends HEAD request to avoid downloading content
- Follows redirects automatically (up to configured limit)
- Handles various HTTP status codes:
  - **200-299**: Valid
  - **300-399**: Valid (redirects followed automatically)
  - **400-403, 405-499**: Valid (accessible but restricted)
  - **404**: Not Found (marked as error)
  - **500+**: Server Error (marked as error)

### 3. Error Handling
- **Connection Errors**: DNS failures, network timeouts
- **Timeout Errors**: Request exceeds configured timeout
- **SSL Errors**: Certificate validation failures
- **Too Many Redirects**: Redirect loop detection

## Configuration

### URLValidator Parameters
```python
URLValidator(
    timeout=10,        # Request timeout in seconds
    max_redirects=10   # Maximum redirects to follow
)
```

### Default Behavior
- Timeout: 10 seconds
- Max redirects: 10
- User-Agent: "DataScope-AI/1.0 (+https://github.com/hericlibong/datascope-ai)"
- SSL verification: Enabled

## Testing

### Unit Tests
- `ai_engine/tests/test_url_validator.py`: Comprehensive validator tests with mocked responses
- `ai_engine/tests/test_pipeline_url_validation.py`: Pipeline integration tests

### Integration Tests
- `test_integration.py`: Real-world validation testing
- `scripts/demo_url_validator.py`: Interactive demonstration

### Running Tests
```bash
# Unit tests (requires test environment setup)
python -m pytest ai_engine/tests/test_url_validator.py

# Integration test (standalone)
python test_integration.py

# Demo
python scripts/demo_url_validator.py
```

## Benefits

1. **Automated Quality Assurance**: Automatically validates all LLM-generated URLs
2. **Error Reporting**: Clear error messages for debugging and manual review
3. **Redirect Handling**: Automatically follows redirects to get final working URLs
4. **Non-invasive**: Failed URLs are marked but not removed
5. **Performance**: Uses HEAD requests to minimize bandwidth
6. **Configurable**: Adjustable timeouts and redirect limits
7. **Logging**: Built-in logging for monitoring and debugging

## Error Categories and Actions

| Status | Description | Action Taken |
|--------|-------------|--------------|
| `valid` | URL is accessible | Use URL as-is |
| `redirected` | URL redirected | Update to final URL |
| `404` | Not found | Mark error, keep URL for review |
| `invalid_url` | Bad format | Mark error, keep URL for review |
| `connection_error` | Network issue | Mark error, keep URL for review |
| `timeout` | Request timeout | Mark error, keep URL for review |
| `server_error` | Server error (5xx) | Mark error, keep URL for review |

## Future Enhancements

Potential improvements for the URL validator:

1. **Retry Logic**: Automatic retries for temporary failures
2. **Batch Processing**: Async validation for multiple URLs
3. **Caching**: Cache validation results to avoid repeated checks
4. **Custom Rules**: Domain-specific validation rules
5. **Content Validation**: Check if URL actually contains data (not just returns 200)
6. **Rate Limiting**: Respect robots.txt and rate limits