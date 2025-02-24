from django.urls import path, include
from . import views
from django.views.generic import TemplateView
app_name = 'users'
urlpatterns = [
    path('sign_up/', views.user_sign_up, name="user_signup"),
    path('login/',views.user_login, name="userlogin"),
    path('', views.homepage, name="home"),
    path('logout/',views.logoutuser, name="logout"),
    path('register/',views.registration, name="register"),      
    path('plans/<int:id>',views.GetAllMessPlan.as_view(), name="get_all_mess_plan"),
    path('payment/<int:id>/', views.PaymentManagement.as_view(), name="process_payment"),
    path('vendors/', views.GetVendors.as_view(), name="get_all_vendors"),
    path('success/',views.success_payment, name="successfull-payment"),
    path('cancel_plan/<int:id>/', views.CancelPlan.as_view(), name="cancel_plan")
]
