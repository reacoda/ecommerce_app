from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """
    Form for user registration with account type selection
    """

    ACCOUNT_TYPES = [
        ("", "Select account type..."),
        ("vendor", "Vendor - I want to sell products"),
        ("buyer", "Buyer - I want to buy products"),
    ]

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"placeholder": "Enter your email address",
                   "class": "form-input"}
        ),
    )

    account_type = forms.ChoiceField(
        choices=ACCOUNT_TYPES,
        required=True,
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "account_type",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add styling to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "style":
                    "width: 100%;"
                    "padding: 10px;"
                    "border: 1px solid #ddd;"
                    "border-radius: 5px;"
                    "font-size: 14px;"
                    "margin-bottom: 5px;"
                }
            )

    def clean_email(self):
        """Check that email is not already in use"""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists")
        return email

    def clean_account_type(self):
        """Validate account type is selected"""
        account_type = self.cleaned_data.get("account_type")
        if not account_type:
            raise forms.ValidationError("Please select an account type")
        return account_type


class LoginForm(AuthenticationForm):
    """
    Form for user login
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add styling to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "style":
                    "width: 100%;"
                    "padding: 10px;"
                    "border: 1px solid #ddd;"
                    "border-radius: 5px;"
                    "font-size: 14px;"
                    "margin-bottom: 5px;",
                    "placeholder": f"Enter your {field_name}",
                }
            )
