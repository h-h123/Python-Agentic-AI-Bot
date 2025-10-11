from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, EmailValidator

class ContactMessage(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text=_("The name of the person sending the message")
    )

    email = models.EmailField(
        _("Email"),
        validators=[EmailValidator()],
        help_text=_("The email address of the sender")
    )

    subject = models.CharField(
        _("Subject"),
        max_length=200,
        validators=[MinLengthValidator(5)],
        help_text=_("The subject of the message")
    )

    message = models.TextField(
        _("Message"),
        validators=[MinLengthValidator(10)],
        help_text=_("The content of the message")
    )

    is_read = models.BooleanField(
        _("Read"),
        default=False,
        help_text=_("Whether the message has been read")
    )

    created_at = models.DateTimeField(
        _("Created At"),
        default=timezone.now,
        help_text=_("When the message was created")
    )

    updated_at = models.DateTimeField(
        _("Updated At"),
        auto_now=True,
        help_text=_("When the message was last updated")
    )

    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["is_read"]),
        ]

    def __str__(self):
        return f"{self.subject} (from {self.name})"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def mark_as_unread(self):
        self.is_read = False
        self.save()