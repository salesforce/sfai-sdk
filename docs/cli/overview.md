# CLI Reference

The SFAI CLI provides a comprehensive set of commands for managing the complete AI application lifecycle, from local development to production deployment and Salesforce AgentForce integration.

## 🚀 Main Command Groups

### `sfai app` - Application Management
Complete application lifecycle management with context-aware operations.

| Command | Description |
|---------|-------------|
| `init` | Initialize a new app with template support |
| `deploy` | Deploy to configured platform (local, Heroku, EKS) |
| `open` | Open app in browser with tunnel support |
| `status` | Show deployment status |
| `logs` | View application logs |
| `delete` | Delete app deployment |
| `context` | Manage application context |
| `publish` | Publish APIs to MuleSoft |
| `helm` | Download Helm charts |

### `sfai platform` - Platform Management
Initialize and switch between deployment platforms.

| Command | Description |
|---------|-------------|
| `init` | Initialize platform configurations (local, Heroku, EKS) |
| `switch` | Switch between configured platforms |

### `sfai config` - Service Configuration
Manage credentials and profiles for external services.

| Command | Description |
|---------|-------------|
| `init` | Configure service credentials (MuleSoft, Heroku, AWS) |
| `update` | Update existing service profiles |
| `list` | List all configured profiles |
| `view` | View profile details |
| `delete` | Delete service profiles |

## 💡 Best Practices

- Use `--interactive` mode for initial setup and complex configurations
- Leverage profiles for managing multiple environments
- Use platform context switching for seamless multi-environment workflows
- Implement CI/CD with non-interactive flags (`--yes`)
- Regular credential rotation using `sfai config update`

---

**Ready to dive in?** Start with the [Commands API Reference](commands.md) for detailed documentation
