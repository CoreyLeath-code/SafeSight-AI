"""Compatibility import for the release-supported FastAPI application.

New integrations should import ``safesight.api:app`` directly. This module is
kept so older deployment commands using ``api.main:app`` continue to work.
"""

from safesight.api import app

__all__ = ["app"]
