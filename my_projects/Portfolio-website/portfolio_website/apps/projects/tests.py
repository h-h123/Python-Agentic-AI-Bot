from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Project, Category, Technology, ProjectImage

User = get_user_model()

class ProjectsModelsTest(TestCase):
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
        self.technology = Technology.objects.create(
            name='Test Technology',
            description='Test technology description',
            icon='fa-test'
        )
        self.project = Project.objects.create(
            title='Test Project',
            slug='test-project',
            author=self.user,
            description='Test description',
            content='Test content',
            status=Project.Status.PUBLISHED,
            project_url='https://example.com',
            source_code_url='https://github.com/example'
        )
        self.project.categories.add(self.category)
        self.project.technologies.add(self.technology)
        self.project_image = ProjectImage.objects.create(
            project=self.project,
            image='test_image.jpg',
            caption='Test image caption'
        )

    def test_category_creation(self):
        self.assertEqual(str(self.category), 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')

    def test_technology_creation(self):
        self.assertEqual(str(self.technology), 'Test Technology')
        self.assertEqual(self.technology.slug, 'test-technology')
        self.assertEqual(self.technology.icon, 'fa-test')

    def test_project_creation(self):
        self.assertEqual(str(self.project), 'Test Project')
        self.assertEqual(self.project.slug, 'test-project')
        self.assertEqual(self.project.status, Project.Status.PUBLISHED)
        self.assertTrue(self.project.published_at is not None)
        self.assertEqual(self.project.project_url, 'https://example.com')
        self.assertEqual(self.project.source_code_url, 'https://github.com/example')

    def test_project_image_creation(self):
        self.assertEqual(str(self.project_image), f'Image for {self.project.title}')
        self.assertEqual(self.project_image.caption, 'Test image caption')

    def test_project_get_absolute_url(self):
        url = self.project.get_absolute_url()
        self.assertEqual(
            url,
            reverse('projects:project_detail', kwargs={'slug': self.project.slug})
        )

class ProjectsViewsTest(TestCase):
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
        self.project = Project.objects.create(
            title='Test Project',
            slug='test-project',
            author=self.user,
            description='Test description',
            content='Test content',
            status=Project.Status.PUBLISHED,
            published_at=timezone.now()
        )
        self.project.categories.add(self.category)

    def test_project_list_view(self):
        response = self.client.get(reverse('projects:project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertTemplateUsed(response, 'projects/project_list.html')

    def test_project_detail_view(self):
        response = self.client.get(self.project.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertTemplateUsed(response, 'projects/project_detail.html')

    def test_category_detail_view(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')
        self.assertTemplateUsed(response, 'projects/category_detail.html')