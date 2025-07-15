# Quickstart

## Before You Start

1. **Create your app folder:** Make sure to create a dedicated folder for your app and run all commands and Python APIs from within that folder.
2. **Ensure Docker is running:** Make sure Docker is running on your local machine before proceeding with any commands or deployments.

## CLI Usage

```bash
# Initialize a new application
sfai app init  # This will download template files into your app folder.

# Deploy to local docker
sfai app deploy

# Access your application in your default browser
sfai app open
```

## Python API Usage

```python
from sfai.app import init, deploy, open

# Initialize a new app
init()

# Deploy the app
deploy()

# Open the app in the browser
open()
```

---

For more advanced usage, see the [CLI Reference](../cli/overview.md) and [Python API Reference](../api/overview.md).
