from django.urls import path, include
from . import views
from django.views.generic import TemplateView
app_name = 'vendor'
urlpatterns = [
    path('delete_menu<int:id>', views.delete_menu, name="delete_menu"),
    path('dashboard/',views.Dashboard.as_view(), name="get_dashboard"),
    path('profile/', views.get_profile, name="get_profile"),
    path('mess/menu/', views.MenuManagement.as_view(), name="get_menu"),
    path('mess/menu/<int:id>/', views.MenuManagement.as_view(), name="get_menu"),
    path('add_menu_item/', views.AddMenuItem.as_view(), name="add_menu_item"),
    path('mess/plan/', views.MessPlan.as_view(), name="get_mess_plan"),
    path('mess/plan/<int:id>/', views.MessPlan.as_view(), name="get_mess_plan"),
    path('remove-item/<int:id>',views.remove_item, name="delete_item"),
    path('get-customer/', views.get_customers, name="get_customers"),
    path('orders/', views.OrderManagement.as_view() , name="get_orders"),
    path('get_select_plans/', views.get_select_item, name="get_select_plans"),
    path('verify_order_otp/',views.changeorderstatus, name="verify_order_otp"),
    path('vendor_transaction/', views.get_transaction, name="mess_transaction"),
    path('vendor_edit_profile/',views.edit_profile, name="edit-vendor-profile"),
    path('refund-transaction/', views.get_refund_transaction, name="refund_vendor_transaction"),
]
