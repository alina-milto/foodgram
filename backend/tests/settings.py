"""Django settings for running tests.

Uses SQLite and a test secret key unless the environment provides
other values (CI sets ``USE_SQLITE=False`` to test against PostgreSQL).
"""

import os

os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('USE_SQLITE', 'True')

from foodgram.settings import *  # noqa: E402,F401,F403
