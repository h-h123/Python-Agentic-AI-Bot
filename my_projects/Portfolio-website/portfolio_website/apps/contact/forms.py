from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator, MinLengthValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

class ContactForm(forms.Form):
    name = forms.CharField(
        label=_("Your Name"),
        max_length=100,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(attrs={
            'placeholder': _('Enter your name'),
            'class': 'form-control',
            'autocomplete': 'name'
        })
    )

    email = forms.EmailField(
        label=_("Your Email"),
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'placeholder': _('Enter your email address'),
            'class': 'form-control',
            'autocomplete': 'email'
        })
    )

    subject = forms.CharField(
        label=_("Subject"),
        max_length=200,
        validators=[MinLengthValidator(5)],
        widget=forms.TextInput(attrs={
            'placeholder': _('Enter the subject of your message'),
            'class': 'form-control'
        })
    )

    message = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(attrs={
            'placeholder': _('Enter your message here...'),
            'class': 'form-control',
            'rows': 5,
            'style': 'resize: vertical; min-height: 150px;'
        }),
        validators=[MinLengthValidator(10)]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'contact-form'
        self.helper.form_id = 'contact-form'
        self.helper.attrs = {'novalidate': ''}

        self.helper.layout = Layout(
            Field('name', css_class='mb-3'),
            Field('email', css_class='mb-3'),
            Field('subject', css_class='mb-3'),
            Field('message', css_class='mb-4'),
            Submit('submit', _('Send Message'), css_class='btn btn-primary')
        )

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        message = cleaned_data.get('message')

        if name and not any(c.isalpha() for c in name):
            self.add_error('name', _("Name must contain letters"))

        if email and not email.endswith(('.com', '.net', '.org', '.io', '.co')):
            self.add_error('email', _("Please enter a valid email address"))

        if message and len(message.split()) < 3:
            self.add_error('message', _("Message should be at least 3 words long"))

        return cleaned_data