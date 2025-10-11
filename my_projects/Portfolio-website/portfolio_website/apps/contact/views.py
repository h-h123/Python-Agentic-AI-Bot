from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .forms import ContactForm
from .models import ContactMessage

class ContactView(FormView):
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:contact_success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Contact Me")
        return context

    def form_valid(self, form):
        # Save the contact message to the database
        contact_message = ContactMessage.objects.create(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message']
        )

        # Send email notification
        subject = f"New Contact Form Submission: {form.cleaned_data['subject']}"
        message = f"""
        You have received a new message from your portfolio website.

        Name: {form.cleaned_data['name']}
        Email: {form.cleaned_data['email']}
        Subject: {form.cleaned_data['subject']}

        Message:
        {form.cleaned_data['message']}
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )

        messages.success(
            self.request,
            _("Thank you for your message! I'll get back to you as soon as possible.")
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            _("There were errors in your form. Please correct them and try again.")
        )
        return super().form_invalid(form)

class ContactSuccessView(TemplateView):
    template_name = 'contact/contact_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Message Sent")
        return context