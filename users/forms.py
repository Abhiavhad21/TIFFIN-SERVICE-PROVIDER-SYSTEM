from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.forms.widgets import TextInput, DateInput
from .models import Subscription, User, Menu, Plans, Order, Messowner
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, QuerySet

class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users.
    Includes all the required fields, plus a repeated password
    """
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    help_text = """Raw passwords are not stored, so there is no way to see this user's password,
                   but you can change the password using <a href="../password/">this form</a>."""
    password = ReadOnlyPasswordHashField(label="Password", help_text=help_text)

    class Meta:
        model = User
        fields = ["email", "password", "user_type", "is_active"]

    def clean_password(self):
        return self.initial["password"]

class UserSignUpForm(forms.ModelForm):
    username = forms.CharField(label= "Enter Username", max_length=40,
            widget=forms.TextInput(attrs={'class':'login_input form-control','required':True}))
    email = forms.EmailField(label="Enter Email", max_length=30, 
            widget=forms.EmailInput(attrs={'class':'login_input form-control','required':True}))
    password = forms.CharField(label="Enter Password",
            widget=forms.PasswordInput(attrs={'class':'login_input form-control','required':True}))
    class Meta:
        model = User
        fields = ['username','email','password']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username')
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email','class':'login_input form-control form-control-lg'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password','class':'login_input form-control form-control-lg'}))
    class META:
        model = User
        fields = ['email','password']

GENDER_CHOICES = [
    ('MALE', 'Male'),
    ('FEMALE', 'Female'),
]
    
class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['email'].initial = instance.email
            self.fields['username'].initial = instance.username

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES, label='Gender',
        widget=forms.RadioSelect(attrs={"class": "gender_check",'required':True}),
    )
    profile_photo = forms.ImageField(widget=forms.FileInput(
        attrs={"class":"form-control", "id":"product_image"}
    ))
    class Meta:
        model = User
        fields = ['email','username','full_name','phone_no','profile_photo','address',
                'city','state','gender','dob']
        widgets = {
            "email": TextInput(
                attrs={"class": "form-control ",'placeholder':'Email',
                        "readonly": True}
            ),
            "username":TextInput(
                attrs={"class":"form-control ", 'placeholder':'username',
                       "readonly": True}
            ),
            "full_name": TextInput(
                attrs={"class": "form-control ",
                       "placeholder":"Full Name",
                       "required":True}
            ),
            "phone_no": TextInput(
                attrs={
                    "oninput":"restrictInputPhone(this)",
                    "class": "form-control ",
                    "placeholder":"Phone Number",
                    "required":True
                },
            ),
            "city":TextInput(
                attrs={"class":"form-control ", "placeholder":"City"}
            ),
            "state":TextInput(
                attrs={"class":"form-control ", "placeholder":"State"}
            ),
            "address": TextInput(
                attrs={"class": "form-control ",
                       "placeholder":"Address House No, street, locality etc,.",
                       "required":True}
            ),
            "dob":DateInput(
                attrs={"class":'form-control', "type":"date",
                        'placeholder':'Date of Birth',
                        'required':True}
            )
        }

    def clean_phone_no(self):
        phone_no = self.cleaned_data.get('phone_no')
        if len(phone_no) < 10:
            raise forms.ValidationError("Phone no should be of 10 digits")
        return phone_no

Menu_Type = [
    ("LUNCH", "Lunch"),
    ("DINNER", "Dinner"),
    ("BOTH", "Both"),
]
  
class MenuForm(forms.ModelForm):

    category = forms.ChoiceField(
        choices=Menu_Type,
        widget=forms.Select(attrs={'class': 'input'})
    )
    image = forms.ImageField(widget=forms.FileInput(
        attrs={"class":"input"}
    ))
    class Meta:
        model = Menu
        fields = ['name',"category",'image',"items",]
        widgets = {
            "name":TextInput(
                attrs={"class":"input",
                       "placeholder":"Item Name",
                       "required":True
                       }
            ),
            "items":TextInput(
                attrs={
                    "class":"input",
                    "placeholder":"Description",
                    "required":True,
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False

Plan_Type = [
    ("LUNCH", "Lunch"),
    ("DINNER", "Dinner"),
    ("BOTH", "Both"),
]

from django.core.validators import validate_integer

class PlansForm(forms.ModelForm):

    price = forms.DecimalField(
        max_digits=9,
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'input decimalInput', 'placeholder': 'Enter price'}),
    )
    duration = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'input integerInput', 'placeholder': 'Enter Duration Days'}),
        validators=[validate_integer]
    )
    plan_type = forms.ChoiceField(
        choices=Plan_Type,
        widget=forms.Select(attrs={'class': 'input'})
    )
    image = forms.ImageField(widget=forms.FileInput(
        attrs={"class":"input"}
    ))
    class Meta:
        model = Plans
        fields = ['plan','subtitle',"description","price",'duration','plan_type','image']
        widgets = {
            "plan":TextInput(
                attrs={"class":"input",
                       "placeholder":"Plan Name",
                       "required":True
                       }
            ),
            "subtitle":TextInput(
                attrs={
                    "class":"input",
                    "placeholder":"Description",
                    "required":True,
                }
            ),
            "description":TextInput(
                attrs={
                    "class":"input",
                    "placeholder":"Benifits and more",
                    "required":True,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False


class OrderForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset=None, label='Select Customer',empty_label="Select Customer",
        widget=forms.Select(attrs={'class':'form-select','id':'select-customer'}))
    class Meta:
        model = Order
        fields = ['customer']
        
    def __init__(self,user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mess = Messowner.objects.filter(vendor=user).first()
        menu = Menu.objects.filter(mess=mess)
        subscription = Subscription.objects.filter(Q(plan_status="ACTIVE") & Q(plan__mess=mess))
        customer_queryset = User.objects.filter(id__in = [subs.customer.id for subs in subscription])
        self.fields["customer"].queryset = customer_queryset
