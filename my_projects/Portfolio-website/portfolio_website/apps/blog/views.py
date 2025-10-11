from django.views.generic import (
    ListView, DetailView, DateDetailView, ArchiveIndexView,
    YearArchiveView, MonthArchiveView, DayArchiveView, TodayArchiveView
)
from django.db.models import Q
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank, TrigramSimilarity
)
from django.utils import timezone
from .models import Post, Category, Tag, Comment
from .forms import CommentForm

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            status=Post.Status.PUBLISHED,
            published_at__lte=timezone.now()
        ).select_related('author').prefetch_related('categories', 'tags')

        if self.request.GET.get('category'):
            queryset = queryset.filter(
                categories__slug=self.request.GET.get('category')
            )

        if self.request.GET.get('tag'):
            queryset = queryset.filter(
                tags__slug=self.request.GET.get('tag')
            )

        return queryset.distinct().order_by('-published_at')

class PostDetailView(DateDetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    date_field = 'published_at'
    month_format = '%m'
    allow_future = False

    def get_queryset(self):
        return super().get_queryset().filter(
            status=Post.Status.PUBLISHED
        ).select_related('author').prefetch_related('categories', 'tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.filter(active=True)
        context['similar_posts'] = Post.objects.filter(
            status=Post.Status.PUBLISHED,
            categories__in=self.object.categories.all()
        ).exclude(id=self.object.id).distinct()[:4]
        return context

class CategoryDetailView(ListView):
    model = Post
    template_name = 'blog/category_detail.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        return super().get_queryset().filter(
            status=Post.Status.PUBLISHED,
            categories=self.category,
            published_at__lte=timezone.now()
        ).select_related('author').prefetch_related('categories', 'tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

class TagDetailView(ListView):
    model = Post
    template_name = 'blog/tag_detail.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['slug'])
        return super().get_queryset().filter(
            status=Post.Status.PUBLISHED,
            tags=self.tag,
            published_at__lte=timezone.now()
        ).select_related('author').prefetch_related('categories', 'tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context

class PostSearchView(ListView):
    model = Post
    template_name = 'blog/post_search.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            search_vector = SearchVector('title', 'content')
            search_query = SearchQuery(query)
            return Post.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(
                search=search_query,
                status=Post.Status.PUBLISHED,
                published_at__lte=timezone.now()
            ).order_by('-rank').select_related('author').prefetch_related('categories', 'tags')
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

def add_comment(request, year, month, day, slug):
    post = Post.objects.get(
        published_at__year=year,
        published_at__month=month,
        published_at__day=day,
        slug=slug
    )

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect(post.get_absolute_url())
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comment_form': form,
        'comments': post.comments.filter(active=True)
    })