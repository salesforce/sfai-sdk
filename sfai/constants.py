from pathlib import Path

CONTEXT_DIR = Path(".sfai")
CONTEXT_FILE = CONTEXT_DIR / "context.json"

GLOBAL_APPS_FILE = Path.home() / ".sfai/apps.json"
CHARTS_PATH = (
    Path(__file__).parent
    / "platform"
    / "providers"
    / "kubernetes"
    / "charts"
    / "default"
)

# CLI UI constants
# Emoji constants
SUCCESS_EMOJI = "✅"
ERROR_EMOJI = "❌"
WARNING_EMOJI = "⚠️"
UPDATE_EMOJI = "🔄"
SECURITY_EMOJI = "🔐"
QUESTION_EMOJI = "❓"
WEB_EMOJI = "🌐"
PORT_EMOJI = "🔌"
LINK_EMOJI = "🔗"
TUNNEL_EMOJI = "🚪"
PACKAGE_EMOJI = "📦"
DOCKER_EMOJI = "🐳"
CONFIG_EMOJI = "⚙️"
# App-specific emojis
APP_NAME_EMOJI = "📁"
TEMPLATE_EMOJI = "📄"
ROCKET_EMOJI = "🚀"
LIGHT_BULB_EMOJI = "💡"
SEARCH_EMOJI = "🔍"
CELEBRATE_EMOJI = "🎉"

# Colors
SUCCESS_COLOR = "green"
ERROR_COLOR = "red"
WARNING_COLOR = "yellow"
INFO_COLOR = "blue"
