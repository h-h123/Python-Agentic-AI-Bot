"""
Initialization file for the portfolio_website apps package.
This package will contain all the individual apps for the portfolio website.
"""

from django.apps import AppConfig

class PortfolioWebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfolio_website.apps'
    verbose_name = "Portfolio Website Apps"

    def ready(self):
        """
        Override this method to perform initialization tasks when the app is ready.
        """
        pass