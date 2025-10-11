from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Post, Category, Tag, Comment

User = get_user_model()

class BlogModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )
        self.tag = Tag.objects.create(name='Test Tag')
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            content='Test content',
            status=Post.Status.PUBLISHED
        )
        self.post.categories.add(self.category)
        self.post.tags.add(self.tag)
        self.comment = Comment.objects.create(
            post=self.post,
            name='Test Commenter',
            email='commenter@example.com',
            content='Test comment'
        )

    def test_category_creation(self):
        self.assertEqual(str(self.category), 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')

    def test_tag_creation(self):
        self.assertEqual(str(self.tag), 'Test Tag')
        self.assertEqual(self.tag.slug, 'test-tag')

    def test_post_creation(self):
        self.assertEqual(str(self.post), 'Test Post')
        self.assertEqual(self.post.slug, 'test-post')
        self.assertEqual(self.post.status, Post.Status.PUBLISHED)
        self.assertTrue(self.post.published_at is not None)

    def test_comment_creation(self):
        self.assertEqual(str(self.comment), 'Comment by Test Commenter on Test Post')
        self.assertTrue(self.comment.active)

    def test_post_get_absolute_url(self):
        url = self.post.get_absolute_url()
        self.assertEqual(
            url,
            reverse('blog:post_detail', kwargs={
                'year': self.post.published_at.year,
                'month': self.post.published_at.month,
                'day': self.post.published_at.day,
                'slug': self.post.slug
            })
        )

class BlogViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            content='Test content',
            status=Post.Status.PUBLISHED,
            published_at=timezone.now()
        )
        self.post.categories.add(self.category)

    def test_post_list_view(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertTemplateUsed(response, 'blog/post_list.html')

    def test_post_detail_view(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertTemplateUsed(response, 'blog/post_detail.html')

    def test_category_detail_view(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')
        self.assertTemplateUsed(response, 'blog/category_detail.html')