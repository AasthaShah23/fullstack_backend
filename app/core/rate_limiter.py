from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize Limiter using client remote IP address as key function
limiter = Limiter(key_func=get_remote_address)

