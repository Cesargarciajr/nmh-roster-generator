from django.contrib.auth.forms import AuthenticationForm
from django import forms

class BulmaAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "input is-medium",
            "placeholder": "Username",
            "autofocus": True,
        })
        self.fields["password"].widget.attrs.update({
            "class": "input is-medium",
            "placeholder": "Password",
        })
