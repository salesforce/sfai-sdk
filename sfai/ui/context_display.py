"""
Rich UI formatting for context display.
"""

from rich.console import Console
from rich.panel import Panel
from sfai.context.manager import ContextManager
from sfai.constants import ERROR_EMOJI, LIGHT_BULB_EMOJI

ctx_mgr = ContextManager()


def display_context(context_data):
    """
    Display the application context with a rich, attractive UI.

    Args:
        context_data: Dictionary containing the context data

    Returns:
        None
    """
    console = Console()

    if not context_data:
        console.print(f"{ERROR_EMOJI} No context found")
        console.print(
            f"{LIGHT_BULB_EMOJI} Run `sfai init app` to initialize your application"
        )
        return

    display_summary(console, context_data)

    active_platform = context_data["active_platform"]
    ctx = ctx_mgr.read_context(active_platform)

    if not ctx:
        console.print(f"{ERROR_EMOJI} No context found")
        console.print(
            f"{LIGHT_BULB_EMOJI} Run `sfai init app` to initialize your application"
        )
        return

    integrations = ["mulesoft", "salesforce", "active_env"]
    integration_config = {}
    for key in integrations:
        if key in ctx and isinstance(ctx[key], dict):
            integration_config[key] = ctx[key]

    # Display the configuration and integrations
    display_configuration(console, ctx, active_platform)
    # display the extracted integrations
    display_integrations(console, integration_config)


def display_summary(console, context_data):
    """Display the context summary panel."""
    app_name = context_data["app_name"]
    active_platform = context_data["active_platform"]

    summary_panel = Panel(
        f"[#f28779]📦 App Name[/]               [#d2a8ff]{app_name}[/]\n"
        f"[#f28779]🌐 Active Platform[/]      [#d2a8ff]{active_platform}[/]",
        title="[bold #3794ff]📄 Context Summary[/]",
        border_style="bright_black",
        expand=True,
    )
    console.print(summary_panel)


def display_configuration(console, context_data, active_platform):
    """Display the configuration section."""
    # Configuration section header
    console.print("\n[#f28779]🔧 Platform Configuration[/]")
    console.print("─" * console.width)

    exclude_keys = ["mulesoft", "salesforce", "active_platform", "app_name"]

    config_keys = [key for key in context_data.keys() if key not in exclude_keys]

    config_content = ""
    # Determine which configuration keys to show based on environment type
    if active_platform.lower() == "aws" or active_platform.lower().startswith("aws-"):
        platform_type = "AWS"
        platform_emoji = "☁️"
    elif active_platform.lower() == "local":
        platform_type = "Local"
        platform_emoji = "💻"
    elif active_platform.lower() == "gcp":
        platform_type = "GCP"
        platform_emoji = "☁️"
    elif active_platform.lower() == "heroku":
        platform_type = "Heroku"
        platform_emoji = "🌐"
    else:
        platform_type = active_platform.title()
        platform_emoji = "🌐"

    # Find the longest key to calculate proper spacing
    if config_keys:
        max_key_length = max([len(key) for key in config_keys])
    else:
        max_key_length = 0

    for key in config_keys:
        value = context_data[key]
        if value is None:
            value = "None"
        # Calculate proper spacing for alignment
        spacing = " " * (max_key_length - len(key) + 4)
        config_content += f"\n[#f28779]{key}[/]{spacing}[#d2a8ff]{value!s}[/]"

    # Remove trailing newline
    if config_content.endswith("\n"):
        config_content = config_content[:-1]

    # Create configuration panel with environment type in title
    config_title = f"[#f28779]{platform_emoji} {platform_type} Platform[/]"
    config_panel = Panel(
        config_content, title=config_title, border_style="bright_black", expand=True
    )
    console.print(config_panel)


def display_integrations(console, integrations):
    """Display the integrations section."""

    # Only display integrations if they exist
    if integrations:
        # Format Integrations similar to Configuration (without box)
        console.print("\n[#f28779]🔌 Integrations[/]")
        console.print("─" * console.width)

        # Process each integration
        for int_name, int_config in integrations.items():
            if isinstance(int_config, dict):
                # Find the longest key in this integration for alignment
                max_int_key_length = max([len(key) for key in int_config.keys()])

                # Create integration panel with all details inside the box
                panel_content = ""
                for key, value in int_config.items():
                    # Mask sensitive information
                    if any(
                        sensitive in key.lower()
                        for sensitive in ["secret", "password", "key", "token"]
                    ):
                        display_value = "********"
                    else:
                        display_value = str(value)

                    # Calculate proper spacing for alignment
                    spacing = " " * (
                        max_int_key_length - len(key) + 4
                    )  # Add 4 extra spaces for padding

                    # Format each line with proper alignment
                    panel_content += (
                        f"[#f28779]{key}[/]{spacing}[#d2a8ff]{display_value}[/]\n"
                    )

                # Remove trailing newline
                if panel_content.endswith("\n"):
                    panel_content = panel_content[:-1]

                # Create and display the integration panel
                int_title = f"[#f28779]{int_name.title()} Integration[/]"
                int_panel = Panel(
                    panel_content,
                    title=int_title,
                    border_style="bright_black",
                    expand=True,
                )
                console.print(int_panel)
