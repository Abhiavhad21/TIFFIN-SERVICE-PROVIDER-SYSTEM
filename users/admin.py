from django.contrib import admin
from .forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Messowner, Menu, Subscription, Order, Plans, Transaction, Gallery

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["id","email", 'username','gender',"profile_photo","full_name","phone_no","user_type"]
    fieldsets = [
        ["Auth", {"fields": ["email", "password"]}],
        ["Personal info", {"fields": ["username",]}],
        ["Settings", {"fields": ["groups", "is_active",'gender','profile_photo',
            "is_staff", "user_type", "is_superuser","address","dob","phone_no",'city',
            'aadhar_no','aadhar_picture','pincode','state','street',
            "is_email_verified"]}],
        ["Important dates", {"fields": ["last_login", "registered_at"]}],
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        [
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "user_type", "password1", "password2"],
            },
        ],
    ]
    search_fields = ["email"]
    ordering = ["email"]
    readonly_fields = ["last_login", "registered_at"]
    list_filter = [
        "user_type",
        "is_active",
        "is_staff",
    ]

admin.site.register(User, UserAdmin)

class MessownerAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'mess_name']

class MenuAdmin(admin.ModelAdmin):
    list_display = ['mess', 'name','image','items','price']

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['customer','plan','end_date','plan_status','total_orders']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer','mess','created_on','status']          
    exclude = ('verify_otp',)
    readonly_fields = ('created_on','status','order_type')
    list_filter = [
        "status",
    ]

class PlansAdmin(admin.ModelAdmin):
    list_display = ['plan', 'plan_type','description','price','image']

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'name', 'payment_to','payment_from']

class GalleryAdmin(admin.ModelAdmin):
    list_display = ['image',]

admin.site.register(Menu, MenuAdmin)
admin.site.register(Messowner, MessownerAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Plans, PlansAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Gallery, GalleryAdmin)