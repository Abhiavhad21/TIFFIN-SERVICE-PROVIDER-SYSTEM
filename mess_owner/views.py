from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from users.forms import MenuForm, PlansForm, OrderForm, UserProfileForm  
from users.models import Messowner, Menu, Plans, Subscription,\
    Order, Transaction, PlanStatus, PlanTypes, User, OrderStatus
from datetime import datetime, timedelta
from django.db.models import Q
import sweetify
from django.utils import timezone   
from users.views import cancel_current_plan

class Dashboard(View):
    def get(self, request):
        mess = Messowner.objects.filter(vendor = request.user).first()
        if not mess:
            return redirect('users:register')
        one_day_ago = timezone.now() - timedelta(days=1)
        subscription = Subscription.objects.filter(Q(plan__mess=mess) & Q(end_date__lte=one_day_ago))
        for subs in subscription:
            cancel_current_plan(request, subs.id)
        orders = Order.objects.filter(mess=mess).order_by('-created_on')
        one_day_ago = timezone.now() - timedelta(days=1)
        orders_in_progress = orders.filter(Q(status="INPROCESS") & Q(created_on__lte=one_day_ago))
        for order in orders_in_progress:
            order.status = 'OUTDATED'
            order.save()
        today = datetime.now().date()
        recent_orders = Order.objects.filter(Q(created_on__date = today) & Q(mess = mess))
        plans = Plans.objects.filter(mess=mess)
        context={
            'mess':mess,
            'recent_orders':recent_orders,
            'plans':plans,
            'subscription':Subscription.objects.filter(plan__mess=mess),
            'customers':mess.mess_customers.all(),
            'orders' :orders.filter(status = OrderStatus.DELIVERED),
            }     
        return render(request, 'profile.html', context)

def get_profile(request):
    return render(request, 'profile.html')

class MenuManagement(View):
    def get(self, request, id=None):
        mess = Messowner.objects.filter(vendor = request.user).first()
        menus = Menu.objects.filter(mess=mess)
        form = MenuForm()
        if id:
            menu = Menu.objects.filter(id=id).first()
            form = MenuForm(instance=menu)
            return render(request, 'update_menu.html',context={"form":form})
        return render(request, 'mess_menus.html', context={'form':form,'menus':menus})
    
    def post(self, request, id=None):
        mess = Messowner.objects.filter(vendor = request.user).first()
        form = MenuForm(request.POST, request.FILES)
        if id:
            menu = Menu.objects.filter(id=id).first()
            form = MenuForm(request.POST, request.FILES, instance=menu)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.mess = mess
            instance.save()
            sweetify.success(request, "Menu Saved Successfull", timer=3000)
            return redirect('vendor:get_menu')
        sweetify.error(request, "Error Couldn't Save", text=f'{form.errors}', timer=10000)
        return redirect(request.META.get('HTTP_REFERER'))


class AddMenuItem(View):
    def get(self,request):
        return render(request, 'add_menu_item.html')

class MessPlan(View):
    def get(self, request, id=None):
        mess = Messowner.objects.filter(vendor = request.user).first()
        plans = Plans.objects.filter(mess=mess)
        form = PlansForm()
        if id:
            plan = Plans.objects.filter(id=id).first()
            form = PlansForm(instance=plan)
            return render(request, 'update_menu.html',context={"form":form})
        return render(request, 'plans_managment.html', context={'form':form,'plans':plans})
    
    def post(self, request, id=None):
        mess = Messowner.objects.filter(vendor = request.user).first()
        form = PlansForm(request.POST, request.FILES)
        if id:
            menu = Plans.objects.filter(id=id).first()
            form = PlansForm(request.POST, request.FILES, instance=menu)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.mess = mess
            instance.save()
            sweetify.success(request,"Successfull",text="Plans Saved")
            return redirect('vendor:get_mess_plan')
        print(form.errors)
        sweetify.error(request, "Error", text="Couldnt created plan",timer=10000)
        return render(request,'plans_managment.html',context={'form':form} )
    
def remove_item(request, id):
    item_type = request.GET.get('item_type')
    if item_type == "plan":
        plan = Plans.objects.filter(id=id).first()
        plan.delete()
    return JsonResponse({'status':"success"},safe=False)

def get_customers(request):
    mess = Messowner.objects.filter(vendor = request.user).first()
    customers = mess.mess_customers.all()
    subscription = Subscription.objects.filter(plan__mess=mess)
    return render(request, 'customer.html', 
            context={'customers':customers, 'subscription':subscription})

class OrderManagement(View):
    def get(self,request):
        mess = Messowner.objects.filter(vendor=request.user).first()
        one_day_ago = timezone.now() - timedelta(days=1)
        subscription = Subscription.objects.filter(Q(plan__mess=mess) & Q(end_date__lte=one_day_ago))
        for subs in subscription:
            cancel_current_plan(request, subs.id)
        orders = Order.objects.filter(mess=mess).order_by('-created_on')
        one_day_ago = timezone.now() - timedelta(days=1)
        orders_in_progress = orders.filter(Q(status="INPROCESS") & Q(created_on__lte=one_day_ago))
        for order in orders_in_progress:
            order.status = 'OUTDATED'
            order.save()
        form = OrderForm(user=request.user)
        return render(request,'mess_order.html', context={'form':form, 'orders':orders})
    
    def post(self, request):
        mess = Messowner.objects.filter(vendor=request.user).first()
        orders = Order.objects.filter(mess=mess)
        plan_type = request.POST.get('order_type')
        menu_id = request.POST.get('menu_type')
        select_customer = request.POST.get('select_customer')
        customers = request.POST.getlist('customer_list')
        try:
            if select_customer == "all":
                customers = Subscription.objects.filter(Q(plan__mess=mess) 
                                    & Q(plan_status = PlanStatus.ACTIVE)
                                    & (Q(plan__plan_type = plan_type)|Q(plan__plan_type = PlanTypes.BOTH)))
            else:
                customers = Subscription.objects.filter(Q(id__in = customers))
            for cstmr in customers:
                Order.objects.create(
                    customer = cstmr.customer,
                    mess = mess,
                    menu = Menu.objects.filter(id=menu_id).first(),
                    status = "INPROCESS",
                    sent_by_vendor = True ,
                    order_type = cstmr.plan
                )
                
            sweetify.success(request, "Success", text="Created order successfully")
            return redirect('vendor:get_orders')
        except Exception:
            sweetify.error(request, "Error", text="Couldnt created orders",timer=10000)
            return render(request, 'mess_order.html', context={'orders':orders})

def get_select_item(request):
    type_ = request.GET.get('type')
    mess = Messowner.objects.filter(vendor=request.user).first()
    if type_ == "Customer":
        customer = request.GET.get('customer')
        plans = Subscription.objects.filter(Q(plan__mess=mess) & Q(customer__id=customer) 
                                            & Q(plan_status = PlanStatus.ACTIVE))
        results = [{'plan_id':plan.plan.id,'plan_type':plan.plan.plan_type} for plan in plans]
        return JsonResponse({'results':results}, safe=False)

    elif type_ == "Order_type":
        plan_type = request.GET.get('plan_type')
        menus = Menu.objects.filter((Q(category = plan_type)| Q(category=PlanTypes.BOTH)) & Q(mess=mess))
        customers = Subscription.objects.filter(Q(plan__mess=mess) & Q(plan_status = PlanStatus.ACTIVE)
                                        & (Q(plan__plan_type = plan_type)|Q(plan__plan_type = PlanTypes.BOTH)))
        menu_items = [{'menu_id':menu.id,'menu_type':f'{menu.name}-{menu.items}'} for menu in menus]
        customer_result = [{'customer_id':customer.id, 'customer':customer.customer.full_name} for customer in customers]
        return JsonResponse({'menus':menu_items,'customers':customer_result}, safe=False)

def changeorderstatus(request):
    id = request.GET.get('verification')
    order = Order.objects.filter(order_id=id).first()
    if order:
        otpfield = request.POST.get('otpfield')
        status = request.POST.get('changeorderstatus')
        if status == "CANCELLED":
            order.status = status
            order.save()
            sweetify.success(request, 'Cancelled', text="Order succesfully Cancelled")
        elif otpfield == order.verify_otp:
            order.status = status
            subscription = Subscription.objects.filter(Q(customer=order.customer) & Q(plan = order.order_type)).first()
            subscription.total_orders = subscription.total_orders-1
            subscription.save()
            order.save()
            sweetify.success(request, 'Delivered', text="Order succesfully ordered")
        else:
            sweetify.error(request, 'Failed', text="OTP didn't matched!")
        return redirect(request.META.get('HTTP_REFERER'))
    sweetify.error(request, 'Failed', text="OTP didn't matched!",timer=10000)
    return redirect(request.META.get('HTTP_REFERER'))
    
def get_transaction(request):
    mess = Messowner.objects.filter(vendor=request.user).first()
    transaction = Transaction.objects.filter(payment_to = mess).order_by('-date')
    context = {
        'transaction':transaction,
    }
    return render(request, 'mess_transaction.html', context)

def get_refund_transaction(request):
    mess = Messowner.objects.filter(vendor=request.user).first()
    transaction = Transaction.objects.filter(refund_from = mess).order_by('-date')
    context = { 
        'transaction':transaction,
    }
    return render(request, 'refund_transaction.html', context)

def edit_profile(request):
    if request.method == "GET":
        user = User.objects.filter(id = request.user.id).first()
        form = UserProfileForm(instance = user)
        return render(request, 'edit_profile.html', context={'form':form})
    else:
        mess_desc = request.POST.get('mess_desc')
        user = User.objects.filter(id = request.user.id).first()
        mess = Messowner.objects.filter(vendor=user).first()
        form = UserProfileForm(request.POST, request.FILES, instance = user)
        if form.is_valid():
            instance = form.save()
            mess.about = mess_desc
            mess.save()
            return redirect('vendor:get_dashboard')
        return redirect(request.META.get('HTTP_REFERER'))
    
def delete_menu(request, id=None):
    menu = Menu.objects.filter(id=id).first()
    menu.delete()
    sweetify.success(request, "Deleted Successfully")
    return redirect(request.META.get('HTTP_REFERER'))
