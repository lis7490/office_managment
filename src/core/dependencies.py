from functools import wraps
import django
from django.db import transaction

def get_db_session():
    """
    Dependency для получения Django DB session
    """
    @wraps
    def dependency():
        with transaction.atomic():
            yield
    return dependency