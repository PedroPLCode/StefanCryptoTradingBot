"""
Blueprint for the main part of the Flask application.

This blueprint is responsible for routing, handling sessions, defining panels, processing context data, 
handling errors, and managing other components necessary for the main functionality of the application.

Imported modules:
- session: Manages session-related functionality.
- panels: Defines panel-related views and functionality.
- context_processors: Provides context data to be injected into templates.
- error_handlers: Defines custom error handlers for the application.
- stefan: Handles additional functionality related to trading bot.
"""
from flask import Blueprint

main = Blueprint('main', __name__)

from . import session, panels, context_processors, error_handlers, stefan