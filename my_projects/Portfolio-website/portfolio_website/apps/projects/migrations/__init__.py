"""
This file is required for Django to recognize the migrations directory for the projects app.
It can be left empty or contain initialization code for migrations.
"""

from django.db.migrations.recorder import MigrationRecorder
from django.db import DEFAULT_DB_ALIAS

# Initialize migration recorder for the projects app
migration_recorder = MigrationRecorder(DEFAULT_DB_ALIAS)

# Optional: Add any initialization code for migrations here if needed
def initialize_migrations():
    """Initialize any custom migration-related functionality."""
    pass