import string
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django import forms


def username_checker(username):
    for letter in username:
        if letter not in string.ascii_letters + '_0123456789':
            raise ValidationError('Разрешены только английские буквы, цифры и знак подчеркивания')
    return username


class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Пароль (подтверждение)', widget=forms.PasswordInput, required=True)
    email = forms.EmailField(label='Адрес электронной почты', required=True)

    def clean_username(self):
        username = self.cleaned_data['username']
        return username_checker(username)

    def clean_email(self):
        email = self.cleaned_data['email']
        user_exists = User.objects.filter(email=email).exists()
        if user_exists:
            raise ValidationError('Пользователь с таким email уже зарегистрирован')
        return email

    def clean(self):
        forms.ModelForm.clean(self)
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise ValidationError({'password2': 'Пароли не совпадают'})

        validate_password(password1)

    def save(self, *args, **kwargs):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password1']
        email = self.cleaned_data['email']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        user = User.objects.create_user(
            username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        return user

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name']
        help_texts = {'username': None}


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(label='Адрес электронной почты', required=True)

    def clean_username(self):
        username = self.cleaned_data['username']
        return username_checker(username)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        help_texts = {'username': None}


class ResetPasswordConfirmForm(forms.Form):
    code = forms.CharField(label='Код из письма', required=True)
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Пароль (подтверждение)', widget=forms.PasswordInput, required=True)

    def __init__(self, *args, valid_code=None, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.valid_code = valid_code

    def clean_code(self):
        code = self.cleaned_data['code']
        if code != self.valid_code:
            raise ValidationError('Неверный код')
        return code

    def clean(self):
        forms.Form.clean(self)
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise ValidationError({'password2': 'Пароли не совпадают'})

        validate_password(password1)
