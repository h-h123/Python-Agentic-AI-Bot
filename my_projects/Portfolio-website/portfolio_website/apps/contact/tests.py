from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.utils import timezone
from .models import ContactMessage
from .forms import ContactForm

class ContactFormTest(TestCase):
    def test_contact_form_valid(self):
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message with more than 10 characters.'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_contact_form_invalid_name(self):
        form_data = {
            'name': '123',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_contact_form_invalid_email(self):
        form_data = {
            'name': 'Test User',
            'email': 'invalid-email',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_contact_form_short_message(self):
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Short'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

class ContactModelTest(TestCase):
    def setUp(self):
        self.contact_message = ContactMessage.objects.create(
            name='Test User',
            email='test@example.com',
            subject='Test Subject',
            message='This is a test message.'
        )

    def test_contact_message_creation(self):
        self.assertEqual(str(self.contact_message), 'Test Subject (from Test User)')
        self.assertFalse(self.contact_message.is_read)
        self.assertIsNotNone(self.contact_message.created_at)

    def test_mark_as_read(self):
        self.contact_message.mark_as_read()
        self.assertTrue(self.contact_message.is_read)

    def test_mark_as_unread(self):
        self.contact_message.mark_as_read()
        self.contact_message.mark_as_unread()
        self.assertFalse(self.contact_message.is_read)

class ContactViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.contact_url = reverse('contact:contact')

    def test_contact_page_status_code(self):
        response = self.client.get(self.contact_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact/contact.html')

    def test_contact_form_submission(self):
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message with more than 10 characters.'
        }
        response = self.client.post(self.contact_url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'New Contact Form Submission: Test Subject')

    def test_contact_form_invalid_submission(self):
        form_data = {
            'name': '',
            'email': 'invalid-email',
            'subject': '',
            'message': 'Short'
        }
        response = self.client.post(self.contact_url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertFormError(response, 'form', 'name', 'This field is required.')
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')
        self.assertFormError(response, 'form', 'subject', 'This field is required.')
        self.assertFormError(response, 'form', 'message', 'Ensure this value has at least 10 characters (it has 5).')