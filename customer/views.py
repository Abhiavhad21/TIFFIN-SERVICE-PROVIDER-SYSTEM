from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from users.forms import MenuForm, PlansForm
from users.models import Messowner, Menu, Plans, Subscription, User, Order, MenuTypes, Transaction, PlanStatus, OrderStatus
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from users.forms import UserProfileForm
import sweetify
from users.views import cancel_current_plan


class Dashboard(View):
    def get(self, request):
        customer = User.objects.filter(id=request.user.id).first()
        # today = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
        one_day_ago = timezone.now() - timedelta(days=1)
        subscription = Subscription.objects.filter(Q(customer=customer) & Q(end_date__lte=one_day_ago))
        for subs in subscription:
            cancel_current_plan(request, subs.id)
        today = datetime.now().date()
        plans = Subscription.objects.filter(Q(plan_status = PlanStatus.ACTIVE) & Q(customer = customer))[:2]
        orders = Order.objects.filter(customer = customer).order_by('-created_on')
        one_day_ago = timezone.now() - timedelta(days=1)
        orders_in_progress = orders.filter(Q(status="INPROCESS") & Q(created_on__lte=one_day_ago))
        for order in orders_in_progress:
            order.status = 'OUTDATED'
            order.save()
        recent_orders = orders.filter(Q(created_on__date = today) & Q(customer = customer))
        context= {    
            'customer':customer,
            'subscription':plans,
            'recent_orders':recent_orders,
            'orders': Order.objects.filter(Q(customer = customer) & Q(status = OrderStatus.DELIVERED))
        }
        return render(request, 'customer/dashboard.html', context)

class CustomerOrders(View):
    def get(self, request):
        customer = User.objects.filter(id=request.user.id).first()
        orders = Order.objects.filter(customer = customer).order_by('-created_on')
        context = {
            'orders':orders,
            'customer':customer,
        }
        return render(request, 'customer/order.html', context)

def get_subscrtiption(request):
    plans = Subscription.objects.filter(customer = request.user).order_by('-created_on')
    context = {
        'subscription':plans,
    }
    return render(request, 'customer/subscription.html', context)

def get_transaction(request):
    transaction = Transaction.objects.filter(payment_from = request.user).order_by('-date')
    context = {
        'transaction':transaction,
    }
    return render(request, 'customer/transaction.html', context)

def get_refund_transaction(request):
    transaction = Transaction.objects.filter(refund_to = request.user).order_by('-date')
    context = { 
        'transaction':transaction,
    }
    return render(request, 'customer/refund_transaction.html', context)

def update_profile(request):
    if request.method == "GET":
        user = User.objects.filter(id = request.user.id).first()
        form = UserProfileForm(instance = user)
        return render(request, 'customer/edit_profile.html',context={'form':form})
    else:
        user = User.objects.filter(id = request.user.id).first()
        form = UserProfileForm(request.POST, request.FILES, instance = user)
        if form.is_valid():
            form.save()
            return redirect('customer:customer_dashboard')
        return redirect(request.META.get('HTTP_REFERER'))

from datetime import time

def cancel_order(request, id=None):
    type_ = request.GET.get('order_type')
    current_time = datetime.now().time()
    comapre_time = ''
    if type_ == MenuTypes.LUNCH:
        comapre_time = time(9, 0, 0)
    elif type_ == MenuTypes.DINNER:
        comapre_time = time(18, 0, 0)
    if current_time < comapre_time:
        order = Order.objects.filter(order_id=id).first()
        order.status = OrderStatus.CANCELLED
        order.save()
        sweetify.success(request, "Order Cancelled", text="Order Cancelled Successfully")
    else:
        sweetify.error(request, "Order cant Cancelled", text="Order cannot be cancelled")
    return redirect('customer:customer_dashboard')

def cancel_plan(request, id=None):
    is_cancelled = cancel_current_plan(request, id)
    if is_cancelled:
        sweetify.success(request, "Succesfull", text="Subscription Cancelled , Refund Processed")
    else:
        sweetify.error(request, "Error", text="Subscription couldn't Cancelled")
    return redirect(request.META.get('HTTP_REFERER'))
