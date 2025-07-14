# SFAI SDK

A powerful toolkit for developing, connecting, and deploying AI applications within the Salesforce ecosystem. Build sophisticated FastAPI-powered AI services, deploy seamlessly to Heroku for native Salesforce integration, publish them to MuleSoft, and connect with Salesforce for enhanced agent capabilities. This SDK simplifies the entire AI application lifecycle—from local development to enterprise deployment on Heroku Private Spaces—with zero configuration, Kubernetes or container support, and secure connectivity between AI services and Salesforce.

## 🚀 Features

- Scaffold a FastAPI app with Docker + Helm support
- Deploy to Kubernetes (local or cloud) using Helm
- Persistent context system for app configuration
- Simplified environment management
- Built-in networking tools (port-forwarding, tunnels)
- MuleSoft API integration
- **Seamless Heroku deployment** for Salesforce ecosystem integration

## Salesforce Ecosystem Integration

SFAI SDK is designed to work natively with the Salesforce ecosystem:

- **Heroku Deployment**: Deploy directly to Salesforce's preferred application platform with enterprise features like Private Spaces and internal routing
- **MuleSoft Connectivity**: Publish and deploy APIs to MuleSoft for Salesforce integration
- **Zero Configuration**: Context system manages all environment settings automatically
- **Enterprise Security**: Support for Salesforce SSO and secure network configurations

## Installation

```bash
pip install sfai
```

### Prerequisites

- Python 3.9+
- Docker
- kubectl
- Helm
- For AWS deployments: AWS CLI configured with appropriate permissions
- For Heroku deployments: Heroku CLI installed

For detailed documentation, see the [SFAI-DOCS](https://git.soma.salesforce.com/pages/da-mle/forge-docs/sfai-sdk/).

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.txt](LICENSE.txt) file for details.
