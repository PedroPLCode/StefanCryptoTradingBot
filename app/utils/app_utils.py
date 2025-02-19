from ..utils.exception_handlers import exception_handler
from flask import Request


@exception_handler(default_return="unknown")
def get_ip_address(request: Request) -> str:
    """
    Retrieves the client's IP address from the request headers.

    Args:
        request (Request): The incoming request object.

    Returns:
        str: The client's IP address. If the 'X-Forwarded-For' header is present,
             it returns the first IP from the list. Otherwise, it returns `request.remote_addr`.
             If an error occurs, it returns 'unknown'.

    Raises:
        Logs an error and sends an admin email if an exception occurs.
    """
    if "X-Forwarded-For" in request.headers:
        return request.headers["X-Forwarded-For"].split(",")[0]
    return request.remote_addr
