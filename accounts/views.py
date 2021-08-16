from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .decorator import *
from django.contrib.auth.models import Group

# Create your views here.
from .models import *
from .forms import OrderForm, createuserForm, CustomerForm
from .filters import OrderFilter

def registerPage(request):
    form = createuserForm()
    if request.method == 'POST':
        form = createuserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # group = Group.objects.get(name='customer')
            # user.groups.add(group)
            # Customer.objects.create(
            #     user=user,
            # )
            messages.success(request,'Account created for '+username)
            return redirect('login')

    context = {'form' : form}
    return render(request,'accounts/register.html',context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,'Username or password is incorrect')

    context = {}
    return render(request,'accounts/login.html',context)

def logoutuser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@admin_only
def home(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()

    total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status= 'delivered').count()
    pending = orders.filter(status ='pending').count()

    context = {
        'orders': orders,'customers': customers,'total_customers': total_customers, 'total_orders': total_orders, 'delivered': delivered,'pending': pending
    }
    return render(request,'accounts/dashboard.html',context)

@allowed_users(allowed_roles=['customer'])
@login_required(login_url='login')
def userpage(request):
    orders = request.user.customer.order_set.all()

    total_orders = orders.count()
    delivered = orders.filter(status='delivered').count()
    pending = orders.filter(status='pending').count()

    print('orders', orders)
    context = {'orders': orders,'total_orders': total_orders, 'delivered': delivered,'pending': pending}
    return render(request, 'accounts/user.html', context)

@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def customers(request,pk):
    customer = Customer.objects.get(id = pk)
    orders = customer.order_set.all()
    total_orders = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context={
        'customers':customer,
        'orders':orders,
        'total_orders':total_orders,
        'myFilter':myFilter,
    }
    return render(request,'accounts/customers.html',context)

@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def products(request):
    products = Product.objects.all()
    return render(request,'accounts/products.html',{'products':products})

@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def create_order(request, pk):

    OrderForemSet = inlineformset_factory(Customer,Order,fields=('product','status'), extra=10 )
    customer = Customer.objects.get(id=pk)
    formset = OrderForemSet(queryset=Order.objects.none(), instance=customer)

    #form = OrderForm(initial={'customer':customer},)

    if request.method == 'POST':
        #form = OrderForm(request.POST)
        formset = OrderForemSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    context = {'form': formset}
    return render(request, 'accounts/order_form.html', context)

@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def update_order(request, pk):

    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    print('ORDER:', order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form' : form}
    return render(request,'accounts/order_form.html', context)

@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def delete_order(request,pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context={'item' : order}
    return render(request, 'accounts/delete.html', context)

@allowed_users(allowed_roles=['customer'])
@login_required(login_url='login')
def account_setting(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST,request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {'form':form}
    return render(request,'accounts/account_setting.html',context)