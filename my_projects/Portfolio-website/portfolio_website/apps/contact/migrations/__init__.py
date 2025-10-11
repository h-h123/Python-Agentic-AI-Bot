"""Initialization file for the contact app migrations.

This file is required for Django to recognize the migrations directory.
It can be left empty or contain initialization code for migrations.
"""

from django.db.migrations.recorder import MigrationRecorder
from django.db import DEFAULT_DB_ALIAS

# Initialize migration recorder for the contact app
migration_recorder = MigrationRecorder(DEFAULT_DB_ALIAS)

def initialize_contact_migrations():
    """Initialize any custom migration-related functionality for the contact app."""
    pass