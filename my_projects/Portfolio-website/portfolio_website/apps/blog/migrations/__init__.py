# Empty migration init file for Django
"""
This file is required for Django to recognize the migrations directory.
It can be left empty or contain initialization code for migrations.
"""

from django.db.migrations.recorder import MigrationRecorder
from django.db import DEFAULT_DB_ALIAS

# Initialize migration recorder for the blog app
migration_recorder = MigrationRecorder(DEFAULT_DB_ALIAS)