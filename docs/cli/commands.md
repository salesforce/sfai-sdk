# CLI Commands API Reference

This page provides comprehensive documentation for all SFAI CLI commands, including arguments, options, and usage examples.

## `sfai app` - Application Management

::: sfai.cli.app.init

**Example:**
```bash
# Initialize with default template
sfai app init

# Initialize with specific template
sfai app init --template fastapi_hello

# Force reinitialize existing app
sfai app init --force --template flask_hello
```

---

::: sfai.cli.app.deploy

**Examples:**
```bash
# Deploy to current platform
sfai app deploy

# Deploy to specific platform
sfai app deploy --platform heroku

# Deploy with custom Helm values
sfai app deploy --values-path ./values.yaml --set-values "image.tag=v1.2.3"

# Deploy to Heroku with commit message
sfai app deploy --platform heroku --commit-message "Feature: Add new API endpoint"
```

---

::: sfai.cli.app.status

**Examples:**
```bash
# Show status from current platform
sfai app status

# Show status from specific platform
sfai app status --platform heroku
```

---

::: sfai.cli.app.logs

**Examples:**
```bash
# Show logs from current platform
sfai app logs

# Show logs from specific platform
sfai app logs --platform eks
```

---

::: sfai.cli.app.delete

**Examples:**
```bash
# Delete from current platform
sfai app delete

# Delete from specific platform
sfai app delete --platform heroku
```

---

::: sfai.cli.app.open

**Examples:**
```bash
# Open app with default settings (opens /docs on port 8080)
sfai app open

# Open specific path
sfai app open --path /api/v1/health

# Open on custom port
sfai app open --port 3000

# Open specific platform
sfai app open --platform heroku --path /api/status
```

---

::: sfai.cli.app.context

**Examples:**
```bash
# Show current context
sfai app context

# Delete current context
sfai app context --delete
```

---

::: sfai.cli.app.publish

**Examples:**
```bash
# Publish with interactive mode
sfai app publish --interactive

# Publish with specific parameters
sfai app publish --name my-api --version 1.0.0 --description "My API" --profile production

# Publish with tags
sfai app publish --name my-api --tags api --tags production --tags v1

# Publish with OpenAPI spec
sfai app publish --name my-api --oas-file ./openapi.yaml --endpoint-uri https://api.example.com
```

---

## `sfai config` - Service Configuration

::: sfai.cli.config.init

**Examples:**
```bash
# Interactive configuration
sfai config init --service mulesoft --interactive

# Direct configuration
sfai config init --service mulesoft --profile-name production \
  --org-id abc123 --environment-id def456 --client-id ghi789 --client-secret secret123

# Use default profile
sfai config init --service mulesoft --org-id abc123 --client-id ghi789 --client-secret secret123
```

---

::: sfai.cli.config.update

**Examples:**
```bash
# Update specific fields
sfai config update --service mulesoft --profile-name production --client-secret new-secret

# Interactive update
sfai config update --service mulesoft --interactive

# Update multiple fields
sfai config update --service mulesoft --org-id new-org --environment-id new-env
```

---

::: sfai.cli.config.list

**Examples:**
```bash
# List all profiles
sfai config list

# List profiles for specific service
sfai config list --service mulesoft
```

---

::: sfai.cli.config.view

**Examples:**
```bash
# View default profile
sfai config view --service mulesoft

# View specific profile
sfai config view --service mulesoft --profile-name production
```

---

::: sfai.cli.config.delete

**Examples:**
```bash
# Delete with confirmation
sfai config delete --service mulesoft --profile-name old-profile

# Force delete without confirmation
sfai config delete --service mulesoft --profile-name old-profile --force
```

---

## `sfai platform` - Platform Management

::: sfai.cli.platform.init

**Examples:**
```bash
# Interactive platform initialization
sfai platform init --interactive

# Initialize Heroku platform
sfai platform init --cloud heroku --app-name my-app --team-name my-team

# Initialize with specific deployment type
sfai platform init --cloud heroku --deployment-type container --routing internal

# Initialize EKS platform
sfai platform init --cloud eks --cluster-name my-cluster --region us-west-2 --namespace production
```

---

::: sfai.cli.platform.switch

**Examples:**
```bash
# Switch to Heroku platform
sfai platform switch heroku

# Switch to local platform
sfai platform switch local

# Switch to EKS platform
sfai platform switch aws
```

---

## Global Options

These options can be used with most commands:

| Option | Description |
|--------|-------------|
| `--help` | Show help message and exit |
| `--version` | Show version information |

---

## Best Practices

### Context Management
- Use `sfai app context` to verify current app and platform settings
- Switch platforms with `sfai platform switch` before deploying
- Delete old contexts with `sfai app context --delete` when switching projects

### Profile Management
- Use descriptive profile names (e.g., `production`, `staging`, `dev`)
- Store different environment credentials in separate profiles
- Use `sfai config list` to see all configured profiles

### Deployment Workflow
1. Initialize app: `sfai app init`
2. Set up platform: `sfai platform init --cloud heroku`
3. Deploy: `sfai app deploy`
4. Check status: `sfai app status`
5. View logs: `sfai app logs`
6. Open app: `sfai app open`

### Interactive Mode
- Use `--interactive` or `-i` for guided setup
- Especially useful for first-time configuration
- Provides validation and helpful prompts

---

## Notes

- **Interactive Mode**: Many commands support `--interactive` or `-i` flag for guided setup
- **Profile Management**: Config commands support multiple profiles per service for different environments
- **Platform Context**: App commands respect the current platform context but can be overridden with `--platform`
- **Required Arguments**: Arguments marked as **Required** must be provided
- **Default Values**: Default values are used when options are not specified
- **Cloudflare Tunnel**: The `--tunnel` option in `sfai app open` requires `cloudflared` to be installed

For more examples and workflows, see the [CLI Examples](examples.md) page.
