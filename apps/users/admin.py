from django import forms
from django.contrib import admin
from django.contrib.auth import models, password_validation, get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext, gettext_lazy as _
from django.utils.html import mark_safe
from ckeditor_uploader.widgets import CKEditorUploadingWidget


User = get_user_model()

class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'
        widgets = {
            'desc': CKEditorUploadingWidget(),
        }


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )

    class Meta:
        model = User
        fields = ("name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})

    def _post_clean(self):
        super()._post_clean()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
        return user


class MyUserAdmin(UserAdmin):
    # form = MyUserChangeForm
    add_form = UserCreationForm
    ordering = ('-id', )

    user_info = ('name', 'avatar', 'mini_openid', 'openid', 'unionid')
    user_info_tuple = user_info 
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': user_info_tuple}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ['id', 'avatar_image', 'name', 'username',]
    search_fields = ['name', 'username']
    list_filter = []
    autocomplete_fields = []
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'avatar', 'password1'),
        }),
    )

    readonly_fields = ['avatar_image']

    def avatar_image(self, obj):
        return mark_safe('<img src="{}" width="150" height="150" />'.format(obj.avatar))

    avatar_image.short_description = '头像'

admin.site.register(User, MyUserAdmin)
