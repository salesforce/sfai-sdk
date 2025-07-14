# sfai/config/api/__init__.py
# Import all API modules
from sfai.config.init import init
from sfai.config.update import update
from sfai.config.list import list
from sfai.config.view import view
from sfai.config.delete import delete
from sfai.config.utils.validate import validate

# from sfai.api import app
# Add other modules as you create them

__all__ = ["delete", "init", "list", "update", "validate", "view"]
