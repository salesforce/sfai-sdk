# SFAI Python API Documentation

Welcome to the SFAI Python API documentation. This section provides comprehensive reference and examples for using SFAI programmatically.

## Quick Navigation

- **[Overview](overview.md)** - Introduction, installation, and quick start
- **[API Reference](modules.md)** - Complete function documentation with parameters
- **[Examples](examples.md)** - Practical usage examples and workflows

## What's New

The Python API documentation has been updated to match the CLI documentation format with:

- ✅ **Auto-generated parameter documentation** - Complete function signatures with types
- ✅ **Comprehensive examples** - Real-world usage patterns and workflows
- ✅ **Consistent formatting** - Matches CLI docs structure and style
- ✅ **Error handling patterns** - Best practices for robust code
- ✅ **Multi-environment workflows** - Development to production examples

## Getting Started

```python
# Install the SDK
pip install sfai-sdk

# Basic usage
from sfai.app import init, deploy, open

# Initialize and deploy an app
result = init(app_name="my-api", template="fastapi_hello")
if result.success:
    deploy()
    open(path="/docs")
```

## API Structure

The SFAI Python API is organized into logical modules:

### `sfai.app` - Application Management
Core application lifecycle functions for initialization, deployment, and management.

### `sfai.config` - Service Configuration
Configuration management for external services like MuleSoft, Heroku, AWS, etc.

### `sfai.core` - Core Models
Shared models and utilities, including the `BaseResponse` class used by all functions.

---

**Next Steps:**
- Read the [Overview](overview.md) for installation and basic concepts
- Browse the [API Reference](modules.md) for detailed function documentation
- Check out [Examples](examples.md) for practical usage patterns
