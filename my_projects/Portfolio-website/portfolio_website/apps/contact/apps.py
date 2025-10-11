from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ContactConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfolio_website.apps.contact'
    verbose_name = _("Contact")

    def ready(self):
        try:
            import contact.signals  # noqa F401
        except ImportError:
            pass