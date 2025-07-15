# FAQ

## What platforms are supported?
- Local Kubernetes, Heroku, AWS EKS, MuleSoft

## How do I configure credentials?
- Use `sfai config init` to set up service profiles for MuleSoft, Heroku, AWS, etc.

## How do I deploy to Heroku?
- Run `sfai platform init --cloud heroku` to configure, then `sfai app deploy`.

## How do I publish to MuleSoft?
- Use `sfai app publish --service mulesoft` with the required options.

## How do I switch platforms easily?
- Use `--platform <platform_name>` with any command to run it in that platform context.

## Where is the app context stored?
- In a `.sfai` directory in your project root.

## How do I get help for a command?
- Run `sfai <command> --help` for detailed usage.

---

For more, see [Troubleshooting](getting-started/installation.md) or open an issue on GitHub.
