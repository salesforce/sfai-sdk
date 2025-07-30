"""
AgentForce integration for SFAI FastAPI applications.

This module provides decorators and metadata classes to automatically generate
OpenAPI specifications with Salesforce AgentForce extensions.
"""

from sfai.core.agentforce.decorators import AgentForceMetadata, agentforce_action

__all__ = ["AgentForceMetadata", "agentforce_action"]
