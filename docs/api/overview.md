# Python API Reference

The SFAI SDK provides a Python API for programmatic control of app lifecycle, deployment, and integration.

## Main API Modules

### `sfai.app` - Application Management

| API | Description |
|---------|-------------|
| `init()` | Initialize a new app with template support |
| `deploy()` | Deploy to configured platform (local, Heroku, EKS) |
| `open()` | Open app in browser with tunnel support |
| `status()` | Show deployment status |
| `logs()` | View application logs |
| `delete()` | Delete app deployment |
| `context()` | Manage application context |
| `publish()` | Publish APIs to MuleSoft |

### `sfai.platform` - Platform Management
Initialize and switch between deployment platforms.

| API | Description |
|---------|-------------|
| `init()` | Initialize platform configurations (local, Heroku, EKS) |
| `switch()` | Switch between configured platforms |

### `sfai.config` - Service Configuration

| API | Description |
|---------|-------------|
| `init()` | Configure service credentials (MuleSoft, Heroku, AWS) |
| `update()` | Update existing service profiles |
| `list()` | List all configured profiles |
| `view()` | View profile details |
| `delete()` | Delete service profiles |

### `sfai.core` - Core Models
- `BaseResponse` — Standard response model for all API calls with `success`, `message`, `error` fields

## Response Format

All API functions return a `BaseResponse` object with the following structure:

```python
class BaseResponse:
    success: bool          # Operation success status
    message: str          # Human-readable message
    error: Optional[str]  # Error message if success=False
    # Additional fields specific to each operation
```

## Error Handling

```python
from sfai.app import deploy

result = deploy()
if result.success:
    print(f"Success: {result.message}")
else:
    print(f"Error: {result.error}")
```

---

See [API Reference](modules.md) for detailed function documentation and [Examples](examples.md) for usage patterns.
