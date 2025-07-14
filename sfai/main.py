from __future__ import annotations

import typer
import logging

# Import app commands
from sfai.cli.app import init as app_init
from sfai.cli.app import deploy as app_deploy
from sfai.cli.app import logs as app_logs
from sfai.cli.app import status as app_status
from sfai.cli.app import delete as app_delete
from sfai.cli.app import context as app_context
from sfai.cli.app import open as app_open
from sfai.cli.app import publish as app_publish
from sfai.cli.app import helm as app_helm

# Import config commands
from sfai.cli.config import init as config_init
from sfai.cli.config import update as config_update
from sfai.cli.config import list as config_list
from sfai.cli.config import view as config_view
from sfai.cli.config import delete as config_delete

# Import platform commands
from sfai.cli.platform import init as platform_init
from sfai.cli.platform import switch as platform_switch


def setup_logging():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )


# Main app
app = typer.Typer(help="SFAI CLI")

# Create app group
app_group = typer.Typer(help="App management commands")
app.add_typer(app_group, name="app")

# create config group
config_group = typer.Typer(
    help=(
        "Service connection configuration, eg. store credentials for "
        "mulesoft, heroku, aws, etc."
    )
)
app.add_typer(config_group, name="config")

# create platform group
platform_group = typer.Typer(help="Platform management commands")
app.add_typer(platform_group, name="platform")

# Add commands to app group - using add_typer for all commands consistently
app_group.add_typer(app_init.app, name="init")
app_group.add_typer(app_deploy.app, name="deploy")
app_group.add_typer(app_logs.app, name="logs")
app_group.add_typer(app_status.app, name="status")
app_group.add_typer(app_delete.app, name="delete")
app_group.add_typer(app_open.app, name="open")
app_group.add_typer(app_context.app, name="context")
app_group.add_typer(app_publish.app, name="publish")
app_group.add_typer(app_helm.app, name="helm")
# Add commands to platform group
platform_group.add_typer(platform_init.app, name="init")
platform_group.command(name="switch")(platform_switch.switch_platform_cmd)
# Add commands to config group
config_group.add_typer(config_init.app, name="init")
config_group.add_typer(config_update.app, name="update")
config_group.add_typer(config_list.app, name="list")
config_group.add_typer(config_view.app, name="view")
config_group.add_typer(config_delete.app, name="delete")
# Export the main CLI entry point for the bin/sfai script to import
main = app

if __name__ == "__main__":
    setup_logging()
    main()
