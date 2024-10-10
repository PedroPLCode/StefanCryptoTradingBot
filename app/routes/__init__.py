from flask import Blueprint

main = Blueprint('main', __name__)

from . import session, panels, context_processors, error_handlers, stefan