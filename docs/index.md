# SFAI SDK Documentation

Welcome to the SFAI SDK! The **complete toolkit** for taking your AI applications from local development all the way to Salesforce AgentForce integration. Build sophisticated AI services with multiple framework support, test changes instantly with Docker-based local deployment, deploy seamlessly to production-ready platforms, and connect directly to Salesforce AgentForce through MuleSoft with **one unified toolkit**.

---

!!! tip "🎯 One SDK, Complete Journey"

    **From `sfai app init` to AgentForce** — Experience the fastest path from idea to production-ready AI agents in the Salesforce ecosystem.

    ✨ **Zero complexity. Maximum impact.**

---

!!! warning "🚧 ACTIVE DEVELOPMENT NOTICE"

    **SFAI SDK is currently in active development.** Features and APIs may change as we continue to enhance the platform.

    If you encounter any issues, please [open a GitHub issue](https://github.com/salesforce/sfai-sdk/issues) or submit a pull request. Feedback and contributions are very welcome!

---

## 🚀 Key Features

=== "🐳 Local Development"

    **Zero-config Docker deployment for instant testing**

    ```bash
    sfai app init     # 📦 Scaffold your app
    sfai app deploy   # 🚀 Deploy locally
    sfai app open     # 🌐 Open in browser
    ```

    ✨ **What you get:**

    - **Zero-config local deployment**: Simple Docker containerization for instant testing
    - **Automatic port management**: Finds available ports and handles networking
    - **Hot reloading**: Test changes immediately without complex setup
    - **Consistent environments**: Same container runs locally and in production-ready platforms

=== "🏭 Production-Ready Platforms"

    **Enterprise-grade platforms ready for scale**

    ```bash
    sfai platform init --cloud heroku  # ⚙️ Configure platform
    sfai app deploy                     # 🚀 Deploy to production
    ```

    🌟 **Supported Platforms:**

    - **Heroku** → Native Salesforce platform integration with Private Spaces support
    - **Amazon EKS** → Kubernetes deployment with auto-scaling and enterprise features
    - **More platforms coming soon** → Expanding cloud provider support

=== "📦 Framework Support"

    **Multiple frameworks, same seamless experience**

    ```bash
    sfai app init --template fastapi_hello  # 🐍 FastAPI (Available Now)
    sfai app init --template flask_hello     # 🌶️ Flask (Coming Soon)
    ```

    🔧 **Current & Upcoming:**

    - **FastAPI** ✅ Currently supported with full Docker + Helm integration
    - **Flask** 🔜 Coming soon with the same seamless deployment experience
    - **Additional frameworks** 🚀 Expanding template library for diverse use cases

=== "🔧 Enterprise Features"

    **Production-ready from day one**

    ```bash
    sfai app publish --service mulesoft  # 🔗 Publish to MuleSoft
    sfai app context                     # 📊 View all configurations
    ```

    💼 **Enterprise-Ready:**

    - **Persistent context system** → Manages all app configuration and deployment state
    - **MuleSoft API integration** → Publish and deploy APIs for Salesforce connectivity
    - **Simplified environment management** → Switch between local, staging, and production
    - **Zero configuration** → Context system handles all environment settings automatically

## 🏆 Why Choose SFAI SDK

!!! abstract "🚀 From Local to AgentForce with one SDK"

    **SFAI SDK provides the only toolkit you need for the complete AI application lifecycle in the Salesforce ecosystem**

=== "🔄 Seamless Integration Pipeline"

    **The fastest path from idea to production-ready AgentForce integration**

    !!! example "Step-by-Step Journey"

        **1️⃣ Start Locally**
        ```bash
        sfai app init && sfai app deploy
        # 🎉 Your app is running at http://localhost:8080
        ```

        **2️⃣ Deploy to Production-Ready Platform**
        ```bash
        sfai platform init --cloud heroku && sfai app deploy
        # 🎉 Your app is live on Heroku with Salesforce integration
        ```

        **3️⃣ Connect to Salesforce**
        ```bash
        sfai app publish --service mulesoft
        # 🎉 Your app is now an AgentForce action available to any agent!
        ```

    ✨ **Key Benefits:**

    - **One command deployment** → Same codebase runs everywhere from your laptop to Salesforce AgentForce
    - **Unified context management** → All configurations, credentials, and deployments managed in one place
    - **Zero friction scaling** → Seamless transition from prototype to enterprise production-ready platforms

=== "🚀 Developer Experience"

    **Why developers choose SFAI SDK over traditional approaches**

    <div class="comparison-grid">

    !!! abstract "With SFAI SDK"
        **Simple. Fast. Integrated.**
        ```bash
        sfai app init           # One tool
        sfai app deploy         # Same commands
        sfai app publish        # Consistent workflow
        ```
        **Result:** 🎉 **Your app is available as an action in AgentForce**

    !!! failure "Traditional Approach"
        **Complex. Slow. Fragmented.**
        ```bash
        # Multiple tools, complex setup
        docker build && kubectl apply && helm install
        # + MuleSoft setup + Salesforce configuration
        # + Environment management + Credential juggling
        ```
        **Result:** 😵 **Weeks of integration work!**

    </div>

    🌟 **Why Developers Love It:**

    - **🛠️ Single SDK** → No need to learn multiple tools, platforms, or deployment processes
    - **🔄 Consistent Workflow** → Same commands work for local testing and production platform deployment
    - **⚡ Instant Feedback** → Test your ai apps locally before deploying to production platforms
    - **🧠 Context Aware** → Remembers your preferences and configurations across all environments

## Salesforce Ecosystem Integration

SFAI SDK is designed to work natively with the Salesforce ecosystem:

- **Heroku Deployment**: Deploy directly to Salesforce's preferred application platform with enterprise features like Private Spaces and internal routing
- **MuleSoft Connectivity**: Publish and deploy APIs to MuleSoft for seamless Salesforce integration
- **AgentForce Integration**: Direct pathway from your AI service to Salesforce AgentForce capabilities
- **Enterprise Security**: Support for Salesforce SSO and secure network configurations
- **Scalable Architecture**: Built for enterprise-grade applications with high availability

---

> **Ready to build?** Follow the [Installation Guide](getting-started/installation.md) to get started, or jump to the [Quickstart](getting-started/quickstart.md) for immediate deployment!

> **Need production deployment?** Check out our [Heroku Deployment](usecases/heroku-deployment.ipynb) and [Local Development](usecases/local-deployment.ipynb) guides.
