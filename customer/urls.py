from django.urls import path, include
from . import views
from django.views.generic import TemplateView
app_name = 'customer'
urlpatterns = [
    path('dashboard/', views.Dashboard.as_view(), name="customer_dashboard"),
    path('customer-orders/',views.CustomerOrders.as_view(), name="customer_orders"),
    path('plans-history/', views.get_subscrtiption, name="get_plans_histroy"),
    path('transaction/', views.get_transaction, name="customer_transaction"),
    path('edit_profile/', views.update_profile, name="update-profile"),
    path('refund_customer/', views.get_refund_transaction, name="refund_customer"),
    path('cancel_order/<int:id>', views.cancel_order, name="cancel_order"),
    path('cancel_plan/<int:id>', views.cancel_plan, name="cancel_plan"),
]
