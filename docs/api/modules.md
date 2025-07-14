# Python API Reference

This page provides comprehensive documentation for all SFAI Python API functions, including parameters, return values, and usage examples.

## `sfai.app` - Application Management

::: sfai.app.init

**Examples:**
```python
from sfai.app import init

# Initialize with default template
result = init()

# Initialize with specific template
result = init(app_name="my-api", template="fastapi_hello")

# Force reinitialize existing app
result = init(force=True, template="flask_hello")
```

---

::: sfai.app.deploy

**Examples:**
```python
from sfai.app import deploy

# Deploy to current platform
result = deploy()

# Deploy to specific platform
result = deploy(platform="heroku")

# Deploy from specific directory
result = deploy(path="./my-app")

# Deploy with additional parameters
result = deploy(platform="heroku", commit_message="Feature: Add new API endpoint")
```

---

::: sfai.app.open

**Examples:**
```python
from sfai.app import open

# Open app with default settings
result = open()

# Open specific path
result = open(path="/api/v1/health")

# Open with tunnel for public access
result = open(tunnel=True)

# Open on custom port
result = open(port=3000)

# Open custom URL
result = open(url="https://my-app.herokuapp.com")
```

---

::: sfai.app.status

**Examples:**
```python
from sfai.app import status

# Show status from current platform
result = status()

# Show status from specific platform
result = status(platform="heroku")
```

---

::: sfai.app.logs

**Examples:**
```python
from sfai.app import logs

# Show logs from current platform
result = logs()

# Show logs from specific platform
result = logs(platform="eks")
```

---

::: sfai.app.delete

**Examples:**
```python
from sfai.app import delete

# Delete from current platform
result = delete()

# Delete from specific platform
result = delete(platform="heroku")
```

---

::: sfai.app.get_context

**Examples:**
```python
from sfai.app import get_context

# Get current context
result = get_context()
if result.success:
    print(f"App: {result.app_name}")
    print(f"Platform: {result.platform}")
```

---

::: sfai.app.delete_context

**Examples:**
```python
from sfai.app import delete_context

# Delete current context
result = delete_context()
```

---

::: sfai.app.publish

**Examples:**
```python
from sfai.app import publish

# Publish to MuleSoft with specific parameters
result = publish(
    service="mulesoft",
    profile="production",
    endpoint_uri="https://api.example.com",
    gateway_id="abc123",
    gateway_version="1.0.0"
)

# Publish with tags
result = publish(
    service="mulesoft",
    name="my-api",
    tags=["api", "production", "v1"]
)
```

---

::: sfai.app.download_helm_chart

**Examples:**
```python
from sfai.app import download_helm_chart

# Download Helm chart for current app
result = download_helm_chart()
```

---

## `sfai.config` - Service Configuration

::: sfai.config.init

**Examples:**
```python
from sfai.config import init

# Initialize MuleSoft configuration
result = init(
    service="mulesoft",
    profile_name="production",
    org_id="abc123",
    environment_id="def456",
    client_id="ghi789",
    client_secret="secret123"
)

# Initialize with config dictionary
config = {
    "org_id": "abc123",
    "client_id": "ghi789",
    "client_secret": "secret123"
}
result = init(service="mulesoft", config=config)
```

---

::: sfai.config.update

**Examples:**
```python
from sfai.config import update

# Update specific fields
result = update(
    service="mulesoft",
    profile_name="production",
    updates={"client_secret": "new-secret"}
)

# Update multiple fields
result = update(
    service="mulesoft",
    updates={
        "org_id": "new-org",
        "environment_id": "new-env"
    }
)
```

---

::: sfai.config.list

**Examples:**
```python
from sfai.config import list

# List all profiles
result = list()

# List profiles for specific service
result = list(service="mulesoft")
```

---

::: sfai.config.view

**Examples:**
```python
from sfai.config import view

# View default profile
result = view(service="mulesoft")

# View specific profile
result = view(service="mulesoft", profile_name="production")
```

---

::: sfai.config.delete

**Examples:**
```python
from sfai.config import delete

# Delete default profile
result = delete(service="mulesoft")

# Delete specific profile
result = delete(service="mulesoft", profile_name="production")
```

---

## `sfai.core` - Core Models

### `BaseResponse`

Standard response model for all API calls.

**Attributes:**
- `success` (bool): Operation success status
- `message` (str): Human-readable message
- `error` (Optional[str]): Error message if success=False
- Additional fields specific to each operation

**Methods:**
- `with_update(**kwargs)`: Create a new response with additional fields

**Example:**
```python
from sfai.app import init

result = init()
print(f"Success: {result.success}")
print(f"Message: {result.message}")
if hasattr(result, 'app_name'):
    print(f"App Name: {result.app_name}")
```
