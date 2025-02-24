from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import random    
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

# Create your models here.
class UniqueIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 9 
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def generate_unique_id(self):
        while True:
            unique_id = random.randint(100000000, 999999999)
            if not User.objects.filter(id=unique_id).exists():
                return unique_id

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if not value:
            value = self.generate_unique_id()
            setattr(model_instance, self.attname, value)
        return value
    
class CreateOtpField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 4 
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def generate_unique_id(self):
        while True:
            unique_id = random.randint(1000, 9999)
            if not Order.objects.filter(verify_otp=unique_id).exists():
                return unique_id

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if not value:
            value = self.generate_unique_id()
            setattr(model_instance, self.attname, value)
        return value


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        user = self.model(
            email=self.normalize_email(email),
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,
            last_login=timezone.now(),
            registered_at=timezone.now(),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        is_staff = extra_fields.pop("is_staff", False)
        is_superuser = extra_fields.pop("is_superuser", False)
        return self._create_user(email, password, is_staff, is_superuser, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(
            email, password, is_staff=True, is_superuser=True, **extra_fields, user_type=User.UserTypes.ADMIN
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.user_type = self.BASE_USER_TYPE
        return super().save(*args, **kwargs)

class User(AbstractBaseUser, PermissionsMixin):
    class GenderTypes(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
           
    class UserTypes(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        VENDOR = "VENDOR", "Vendor"
        CUSTOMER = "CUSTOMER", "Customer"

    BASE_USER_TYPE = UserTypes.CUSTOMER
    username = models.CharField(verbose_name="Username", unique=True, max_length=30, null=True, blank=True)
    email = models.EmailField(verbose_name="Email", unique=True, max_length=255)
    id = UniqueIDField(primary_key=True)
    is_active = models.BooleanField(verbose_name="Active", default=True)
    is_staff = models.BooleanField(verbose_name="Staff", default=False)
    registered_at = models.DateTimeField(verbose_name="Registered at", auto_now_add=timezone.now)
    user_type = models.CharField(
        verbose_name=("User Type"), max_length=100, choices=UserTypes.choices, blank=True,
    )
    is_email_verified = models.BooleanField(default=False)
    full_name = models.CharField(verbose_name="Full Name",  max_length=30, null=True, blank=True)
    roll_no = models.CharField(max_length=50, null=True, blank=True, default="")
    year = models.DateField(blank=True, null=True)
    aadhar_no = models.CharField(max_length=16, blank=True, null=True)
    aadhar_picture = models.ImageField(verbose_name="Aadhar Picture", blank=True, null=True)
    phone_no = models.CharField(verbose_name="Phone number", unique=True, max_length=12, null=True, blank=True)
    dob = models.DateField(verbose_name="Date of Birth", blank=True, null=True)
    is_phone_no_verified = models.BooleanField(verbose_name="Phone number verified", default=False)
    profile_photo = models.ImageField(upload_to="user_images", verbose_name="Profile Pic", blank=True)
    gender = models.CharField(verbose_name=("Gender Type"), max_length=20,
                              choices=GenderTypes.choices,  blank=True, null=True)
    reg_number = models.CharField(max_length=50, verbose_name="Registration Number", blank=True, null=True)
    start_date = models.DateField(auto_created=False, blank=True, null=True)
    end_date = models.DateField(auto_created=False, blank=True, null=True)
    address = models.TextField(max_length=300, blank=True, null=True)
    pincode=models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    street = models.CharField(max_length=200, blank=True, null=True)
    # Fields settings
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    objects = UserManager()
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        
class Messowner(models.Model):
    vendor = models.ForeignKey(User,verbose_name="Vendor", on_delete=models.CASCADE)
    mess_name = models.CharField(verbose_name="Mess Name", max_length=100, blank=True,null=True)
    mess_customers = models.ManyToManyField(User, related_name="customers",
                                            verbose_name="Customer", blank=True)
    employees = models.ManyToManyField(User,related_name="mess_workers",
                                        verbose_name="Mess Worker", blank=True)
    about = models.CharField(max_length=400, verbose_name="About", blank=True)
    
    class Meta:
        verbose_name = "Vendor's Mess"
        verbose_name_plural = "Mess Details"
    
    def __str__(self):
        return f'{self.mess_name}'

class PlanTypes(models.TextChoices):
    LUNCH = "LUNCH", "Lunch"
    DINNER = "DINNER", "Dinner"
    BOTH = "BOTH", "Both"

class Plans(models.Model):
    mess = models.ForeignKey(Messowner,verbose_name="Mess Name", on_delete=models.CASCADE)
    plan = models.CharField(max_length=100,blank=True, null= True)
    plan_type = models.CharField(verbose_name=("Plan Type"), max_length=100, 
                                choices=PlanTypes.choices, blank=True,)
    price = models.CharField(max_length=100, blank=True, null= True)
    description = models.CharField(max_length=1000, blank= True, null= True)
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to="mess_plan_images",verbose_name="Plan image", default="default/dabba_express_logo.png", blank=True)
    duration = models.IntegerField(blank=True)
    def __str__(self):
        return f'{self.plan_type}'

class MenuTypes(models.TextChoices):
    LUNCH = "LUNCH", "Lunch"
    DINNER = "DINNER", "Dinner"
    BOTH = "BOTH", "Both"

class Menu(models.Model):
    name = models.CharField(max_length=50, verbose_name="Dish Name",blank=True, null=True)
    mess = models.ForeignKey(Messowner, verbose_name="Mess Name", on_delete=models.CASCADE)
    price = models.CharField(max_length=20, verbose_name="Price", blank=True, null=True)
    items = models.TextField(verbose_name="Dishes", blank=True, null=True)
    image = models.ImageField(upload_to="mess_menu_images",verbose_name="Item image", blank=True, default="default/mess_menu.jpg")
    category = models.CharField(verbose_name=("Category"), max_length=100, 
                                choices=MenuTypes.choices, blank=True,)
    def __str__(self):
        return f'{self.name}-{self.items}'

class PlanStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    EXPIRED = "EXPIRED", "Expired"

class Subscription(models.Model):
    customer = models.ForeignKey(User, verbose_name="Customer", on_delete=models.CASCADE)
    plan = models.ForeignKey(Plans, on_delete=models.SET_NULL, verbose_name="Plan", null=True)
    end_date = models.DateField(auto_created=False, blank=True)
    plan_status = models.CharField(max_length=50,verbose_name="Plan Status", choices=PlanStatus.choices)
    total_orders = models.IntegerField(default=0,verbose_name="Order Quota")
    created_on = models.DateTimeField(auto_created=True, auto_now=True, verbose_name="Activation Date")
 
class OrderStatus(models.TextChoices):
    DELIVERED = "DELIVERED", "Delivered"
    ORDERED = "ORDERED", "Ordered"      
    INPROCESS = "INPROCESS", "In Process"
    CANCELLED = "CANCELLED", "Cancelled"
    OUTDATED = "OUTDATED", "Out Dated"

class Order(models.Model): 
    order_id = UniqueIDField(primary_key=True)
    mess = models.ForeignKey(Messowner, verbose_name="Mess", on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, verbose_name="Order Items", on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Customer")
    status = models.CharField(max_length=50,verbose_name="Order Status", choices=OrderStatus.choices)
    sent_by_vendor = models.BooleanField(blank=True, null=True)
    verify_otp = CreateOtpField(auto_created=True)
    created_on = models.DateTimeField(auto_created=True, auto_now=True)
    order_type = models.ForeignKey(Plans, verbose_name="Order Type",on_delete=models.CASCADE)

class PaymentStatus(models.TextChoices):
    SUCCESS = "SUCCESS","Success"
    FAILED = "FAILED","Failed"
    PENDING = "PENDING","Pending"
    REFUND = "REFUND", "Refunded"

class Transaction(models.Model):
    name = CharField(_("Customer Name"), max_length=254, blank=False, null=False)
    amount = models.FloatField(_("Amount"), null=False, blank=False)
    status = models.CharField(
        _("Payment Status"),
        default=PaymentStatus.PENDING,
        choices=PaymentStatus.choices,
        max_length=254,
        blank=False,
        null=False,
    )
    payment_id = UniqueIDField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    payment_to = models.ForeignKey(Messowner,
                                   related_name="payment_to", blank=True,
                                   on_delete=models.CASCADE, null=True)
    payment_from = models.ForeignKey(User, 
                                     related_name="payment_from", blank=True,
                                     on_delete=models.CASCADE, 
                                     null=True
                                    )
    refund_from = models.ForeignKey(Messowner,
                        related_name="refund_from", blank=True,
                        on_delete=models.CASCADE,
                        null=True)
    refund_to = models.ForeignKey(User, 
                        related_name="refund_to", blank=True,
                        on_delete=models.CASCADE, 
                        null=True)
    
    def __str__(self):
        return f"{self.payment_id}-{self.name}-{self.status}"
    
class Gallery(models.Model):
    image = models.ImageField(verbose_name="Gallery image", blank=True, null=True)