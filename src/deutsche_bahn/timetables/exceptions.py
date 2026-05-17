# Re-export from the shared exceptions module so both subpackages share the same classes.
from deutsche_bahn.exceptions import AuthenticationError, DBApiError, NotFoundError, RateLimitError

__all__ = ["DBApiError", "AuthenticationError", "NotFoundError", "RateLimitError"]
