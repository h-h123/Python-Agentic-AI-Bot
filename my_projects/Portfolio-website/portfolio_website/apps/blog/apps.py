from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfolio_website.apps.blog'
    verbose_name = _("Blog")

    def ready(self):
        try:
            import blog.signals  # noqa F401
        except ImportError:
            pass