from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Category(models.Model):
    name = models.CharField(_("Category Name"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("projects:category_detail", kwargs={"slug": self.slug})

class Technology(models.Model):
    name = models.CharField(_("Technology Name"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)
    icon = models.CharField(_("Icon Class"), max_length=50, blank=True, help_text=_("Font Awesome or similar icon class"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Technology")
        verbose_name_plural = _("Technologies")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("projects:technology_detail", kwargs={"slug": self.slug})

class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DF", _("Draft")
        PUBLISHED = "PB", _("Published")
        ARCHIVED = "AR", _("Archived")

    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=200, unique=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name=_("Author")
    )
    description = models.TextField(_("Description"))
    content = models.TextField(_("Content"), blank=True)
    status = models.CharField(
        _("Status"),
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT
    )
    categories = models.ManyToManyField(
        Category,
        related_name="projects",
        verbose_name=_("Categories"),
        blank=True
    )
    technologies = models.ManyToManyField(
        Technology,
        related_name="projects",
        verbose_name=_("Technologies"),
        blank=True
    )
    featured_image = models.ImageField(
        _("Featured Image"),
        upload_to="projects/images/%Y/%m/%d/",
        blank=True,
        null=True
    )
    project_url = models.URLField(_("Project URL"), blank=True, null=True)
    source_code_url = models.URLField(_("Source Code URL"), blank=True, null=True)
    created_at = models.DateTimeField(_("Created At"), default=timezone.now)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    published_at = models.DateTimeField(_("Published At"), null=True, blank=True)
    is_featured = models.BooleanField(_("Is Featured"), default=False)

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["-published_at"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("projects:project_detail", kwargs={"slug": self.slug})

class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Project")
    )
    image = models.ImageField(
        _("Image"),
        upload_to="projects/gallery/%Y/%m/%d/"
    )
    caption = models.CharField(_("Caption"), max_length=200, blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    is_featured = models.BooleanField(_("Is Featured"), default=False)

    class Meta:
        verbose_name = _("Project Image")
        verbose_name_plural = _("Project Images")
        ordering = ["-is_featured", "created_at"]

    def __str__(self):
        return f"Image for {self.project.title}"