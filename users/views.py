from django.shortcuts import render
from .models import Gallery, Transaction, User, Messowner, Plans, Menu, Subscription, PlanTypes
from .forms import UserSignUpForm, LoginForm, UserProfileForm
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login,logout
from django.http import Http404
from django.views import View
from django.db.models import Q
import sweetify
from datetime import datetime, timedelta
from django.utils import timezone

def user_sign_up(request):
    if request.method == "GET":
        form = UserSignUpForm()
        return render(request,'sign_up.html', context={'form':form})
    else:
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            userType = request.POST.get('user_type')
            user.user_type = userType
            user.save()
            login(request, user)
            return redirect('users:register')
        else:
            return render(request, 'sign_up.html', context={'form':form})

from django.contrib import messages

def user_login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'user_login.html', context={'form':form})
    else:
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                one_day_ago = timezone.now() - timedelta(days=1)
                subscription = Subscription.objects.filter(Q(customer=user) & Q(end_date__lte=one_day_ago))
                for subs in subscription:
                   cancel_current_plan(request, subs.id)
                return redirect('users:home')
            messages.error(request, "Invalid username or password!")
        else:
            messages.error(request, "Please Fill Correct Information!")
        return render(request,'user_login.html', context={'form':form})
        
def logoutuser(request):
    logout(request)
    return redirect('/')

def registration(request):
    if not request.user.is_authenticated:
        form = UserSignUpForm()
        return redirect('users:user_signup')
    instance = User.objects.filter(id = request.user.id).first()
    if request.method == "GET":
        form = UserProfileForm(instance=instance)
        return render(request,'registration_form.html', context={'form':form})
    else:
        form = UserProfileForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            if request.user.user_type == "VENDOR":
                mess_name = request.POST.get('mess_name')
                Messowner.objects.create(vendor=instance, mess_name=mess_name)
                return redirect('vendor:get_dashboard')
            return redirect('users:home')
        else:
            messages.error(request, form.errors)
            return render(request, 'registration_form.html', context={'form':form})
        
def homepage(request):
    gallery = Gallery.objects.all()
    plans = Plans.objects.all()[:5]
    if request.user.is_authenticated:
        one_day_ago = timezone.now() - timedelta(days=1)
        subscripton = Subscription.objects.filter(Q(customer=request.user) & Q(end_date__lte=one_day_ago))
        for subs in subscripton:
            cancel_current_plan(request, subs.id)
    context={
        'gallery':gallery,
        'plans':plans,
    }
    return render(request,'index.html', context)

class GetAllMessPlan(View):
    def get(self, request, id=None):
        plans = Plans.objects.filter(mess__id = id)
        mess = Messowner.objects.filter(id=id).first()
        menus = Menu.objects.filter(mess__id = id)
        return render(request, 'all_mess_plans.html', context={'plans':plans,'mess':mess,'menus':menus})

class PaymentManagement(View):
    def get(self, request, id=None):
        plan = Plans.objects.filter(id=id).first()
        exist_plan = Subscription.objects.filter(Q(plan__id=id) & Q(customer = request.user) & Q(plan_status = "ACTIVE"))
        active_plans = Subscription.objects.filter(Q(customer = request.user) & Q(plan_status = "ACTIVE"))
        if exist_plan: 
            sweetify.info(self.request, 'You already subscribed This plan')
            return redirect(request.META.get('HTTP_REFERER'))

        if len(active_plans) == 2:
            context ={
                'plans':active_plans,
                'vendor_id':plan.mess.id,
            }
            return render(request, 'cancel_plan.html', context)
        plan = Plans.objects.filter(id=id).first()
        context={
            'plan':plan,
        }
        return render(request, 'payment.html', context)
    
    def post(self, request, id=None):
        amount = request.POST.get('plan_price')
        plan = Plans.objects.filter(id=id).first()
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=plan.duration)
        customer = User.objects.filter(id=request.user.id).first()
        Transaction.objects.create(
            name = customer.username,
            amount = amount,
            status = "SUCCESS",
            payment_to = plan.mess,
            payment_from = customer   
        )
        Subscription.objects.create(
            plan = plan,
            customer = request.user, 
            end_date = end_date,  
            plan_status = "ACTIVE",
            total_orders = plan.duration if plan.plan_type != "BOTH" else 2*plan.duration,
        )
        plan.mess.mess_customers.add(customer)
        plan.mess.save()
        return render(request, 'pending_payment.html')
   
class GetVendors(View):
    def get(self, request):
        vendors = Messowner.objects.all()
        context = {
            'vendors':vendors,
        }
        return render(request, 'all_vendors.html', context=context)
            
    def post(self, request):
        search_query = request.POST.get('search_query')
        search_query = search_query.lower()
        vendors = Messowner.objects.filter(Q(mess_name__icontains = search_query)
                                        | Q(vendor__address__icontains = search_query) 
                                        | Q(vendor__city__icontains = search_query)
                                        | Q(vendor__full_name__icontains = search_query))
        context = {
                'vendors':vendors,
                'search_query':search_query,
            }
        return render(request, 'all_vendors.html', context=context)

def success_payment(request):
    sweetify.success(request, "Payment Successfull", text="Your payment is successfull")
    return render(request, 'payment_succes.html')

def cancel_current_plan(request, id):
    try:
        subs = Subscription.objects.filter(id=id).first()
        refund = subs.total_orders
        if subs.plan.plan_type == PlanTypes.BOTH:
            refund = refund/2
        subs.plan_status = "EXPIRED"
        subs.total_orders = 0
        subs.save()
        plan_price = float(subs.plan.price)/subs.plan.duration
        refund = refund*plan_price
        customer = User.objects.filter(id=subs.customer.id).first()
        if refund > 0:
            Transaction.objects.create(
                name = customer.username,
                amount = '{:.2f}'.format(refund),
                status = "REFUND",
                refund_from = subs.plan.mess,
                refund_to = customer,
            )
        return True
    except Exception:
        return False

class CancelPlan(View):
    def get(self, request, id=None):
        vendor_id = request.GET.get('uid')
        is_flag = cancel_current_plan(request, id)
        if is_flag:
            sweetify.success(request, "Plan Deactivated", text="Refund Credited Successfully")
            return redirect('users:get_all_mess_plan', vendor_id)
        else:
            sweetify.error(request, 'Error', text="Couldnt Deactivated")
            return redirect(request.META.get('HTTP_REFERER'))


