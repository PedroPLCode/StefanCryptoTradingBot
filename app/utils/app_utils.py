from .logging import logger
from ..utils.email_utils import send_admin_email

def get_ip_address(request):
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
    try:
        if 'X-Forwarded-For' in request.headers:
            return request.headers['X-Forwarded-For'].split(',')[0]
        return request.remote_addr
    
    except Exception as e:
        logger.error(f"Exception in get_ip_address: {str(e)}")
        send_admin_email('Exception in get_ip_address', str(e))
        return 'unknown'