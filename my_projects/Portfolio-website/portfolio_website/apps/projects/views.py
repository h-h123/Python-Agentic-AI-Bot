from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.utils import timezone
from .models import Project, Category, Technology

class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            status=Project.Status.PUBLISHED,
            published_at__lte=timezone.now()
        ).select_related('author').prefetch_related(
            'categories', 'technologies', 'images'
        ).order_by('-is_featured', '-published_at')

        if self.request.GET.get('category'):
            queryset = queryset.filter(
                categories__slug=self.request.GET.get('category')
            )

        if self.request.GET.get('technology'):
            queryset = queryset.filter(
                technologies__slug=self.request.GET.get('technology')
            )

        return queryset.distinct()

class FeaturedProjectListView(ListView):
    model = Project
    template_name = 'projects/featured_project_list.html'
    context_object_name = 'projects'
    paginate_by = 3

    def get_queryset(self):
        return super().get_queryset().filter(
            status=Project.Status.PUBLISHED,
            is_featured=True,
            published_at__lte=timezone.now()
        ).select_related('author').prefetch_related(
            'categories', 'technologies', 'images'
        ).order_by('-published_at')

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return super().get_queryset().filter(
            status=Project.Status.PUBLISHED,
            published_at__lte=timezone.now()
        ).select_related('author').prefetch_related(
            'categories', 'technologies', 'images'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_projects'] = Project.objects.filter(
            status=Project.Status.PUBLISHED,
            published_at__lte=timezone.now()
        ).exclude(id=self.object.id).filter(
            Q(categories__in=self.object.categories.all()) |
            Q(technologies__in=self.object.technologies.all())
        ).distinct()[:4]
        return context

class CategoryDetailView(ListView):
    model = Project
    template_name = 'projects/category_detail.html'
    context_object_name = 'projects'
    paginate_by = 6

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        return super().get_queryset().filter(
            status=Project.Status.PUBLISHED,
            categories=self.category,
            published_at__lte=timezone.now()
        ).select_related('author').prefetch_related(
            'categories', 'technologies', 'images'
        ).order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

class TechnologyDetailView(ListView):
    model = Project
    template_name = 'projects/technology_detail.html'
    context_object_name = 'projects'
    paginate_by = 6

    def get_queryset(self):
        self.technology = Technology.objects.get(slug=self.kwargs['slug'])
        return super().get_queryset().filter(
            status=Project.Status.PUBLISHED,
            technologies=self.technology,
            published_at__lte=timezone.now()
        ).select_related('author').prefetch_related(
            'categories', 'technologies', 'images'
        ).order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['technology'] = self.technology
        return context