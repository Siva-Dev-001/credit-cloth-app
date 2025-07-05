from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Min, Max
from retailapp.forms import InventoryItemForm 
from retailapp.models import Customer, DressPurchase, Payment, ReturnOrExchange, PurchaseItem, InventoryItem, ReturnRequest, ExchangeRequest
import boto3
from django.conf import settings
from django.utils.timezone import now
from collections import OrderedDict
from urllib.parse import quote_plus
from collections import defaultdict

def get_sns_client():
    return boto3.client(
        'sns',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )


# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['userid'] = user.pk
            request.session['username'] = user.username
            request.session['email'] = user.email
            request.session['last_seen'] = now().isoformat()
            # messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Credentials')
            return render(request, 'accounts/auth-login.html')
    return render(request, 'accounts/auth-login.html')

# Logout view
def logout_view(request):
    logout(request)
    request.session.flush()
    messages.info(request, 'You are logged out. Login to continue')
    return redirect('login')

# Dashboard view
@login_required
def dashboard(request):
    customers_count = Customer.objects.count()
    customers = Customer.objects.all()
    purchases_count = DressPurchase.objects.count()
    payments_all = Payment.objects.count()
    pay_history = Payment.objects.all()
    due_total = sum([p.due_amount for p in DressPurchase.objects.all()])

    customer_data = []
    for customer in customers:
        purchases = DressPurchase.objects.filter(customer=customer)
        
        total_purchased = purchases.aggregate(total=Sum('total_amount'))['total'] or 0
        total_paid = sum(p.paid_amount for p in purchases)  # paid_amount property!
        pending_due = total_purchased - total_paid
        
        first_purchase = purchases.aggregate(first_date=Min('purchase_date'))['first_date']
        
        payments = Payment.objects.filter(purchase__customer=customer)
        last_payment = payments.aggregate(last_date=Max('payment_date_time'))['last_date']
        
        customer_data.append({
            'customer': customer,
            'total_purchased': total_purchased,
            'total_paid': total_paid,
            'pending_due': pending_due,
            'first_purchase': first_purchase,
            'last_payment': last_payment,
        })
    

    payments = Payment.objects.select_related('purchase__customer').order_by('-payment_date')[:5] # only display last 5 payments
    paginator = Paginator(payments, 5)  # 10 payments per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'customers': customers, 'customer_data': customer_data[:5],
        'customer_count': customers_count,
        'purchase_count': purchases_count,
        'payment_count': payments_all, 'segment': 'dashboard',
        'total_due': due_total, 'pay_history': pay_history, 'page_obj': page_obj
    }
    return render(request, 'pages/dashboard.html', context)

@login_required
def list_pending_dues(request):
    customers = Customer.objects.all()
    customer_data = []
    for customer in customers:
        purchases = DressPurchase.objects.filter(customer=customer)
        
        total_purchased = purchases.aggregate(total=Sum('total_amount'))['total'] or 0
        total_paid = sum(p.paid_amount for p in purchases)  # paid_amount property!
        pending_due = total_purchased - total_paid
        
        first_purchase = purchases.aggregate(first_date=Min('purchase_date'))['first_date']
        
        payments = Payment.objects.filter(purchase__customer=customer)
        last_payment = payments.aggregate(last_date=Max('payment_date_time'))['last_date']
        
        customer_data.append({
            'customer': customer,
            'total_purchased': total_purchased,
            'total_paid': total_paid,
            'pending_due': pending_due,
            'first_purchase': first_purchase,
            'last_payment': last_payment,
        })
    paginator = Paginator(customer_data, 10)  # 10 payments per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'customers': customers, 'customer_data': customer_data, 'page_obj': page_obj}
    return render(request, 'pages/list_pending_dues.html', context)   

def default_no_payment_message(customer_name):
    return (
        f"வணக்கம் {customer_name}, இன்று எந்தக் கட்டணமும் பெறப்படவில்லை. "
        f"தயவு செய்து நிலுவை தொகையை விரைவில் செலுத்துங்கள். நன்றி – SK Dresses."
    )


@login_required
def list_payments(request):
    payments_count = Payment.objects.count()
    payments = Payment.objects.select_related('purchase__customer').order_by('-payment_date')
    payment_data = []
    red_heart = '' # '\u2764\uFE0F'
    star = '' #"\U0001F31F"
    folded_hands = '' #"\U0001F64F"
    location = '' #"\U0001F4CD"
    recepit = '' #"\U0001F9FE"
    ccard = '' #"\U0001F4B3"
    calendar = '' #"\U0001F4C5"
    pushupin = '' #"\U0001F4CC"
    check_mark = '' #"\u2705"

    for payment in payments:
        customer = payment.purchase.customer
        purchase = payment.purchase
        date = payment.payment_date.strftime("%d-%b-%Y")
        if payment.payment_type not in ["No Cash" ,"Discount"]:
            msg = f"{star} அன்பார்ந்த வாடிக்கையாளர் {customer.name} அவர்களுக்கு வணக்கம்!\n"
            # msg += f"🙏 எங்களின் சேவையை நம்பி தொடர்வதற்கு நன்றிகள்!\n"
            msg += f"\n{folded_hands} நீங்கள் எங்களை தேர்ந்தெடுத்து, நம்பிக்கையுடன் தொடர்வது எங்களுக்கு பெருமை! \n"
            
            msg += f"\n{recepit} வாங்கிய பொருட்கள் தொகை: ₹{purchase.total_amount}"
            msg += f"\n{ccard} இன்று செலுத்தியது: ₹{payment.amount_paid} ({payment.payment_type})"
            msg += f"\n{calendar} தேதி: {date}"
            msg += f"\n{pushupin} தற்போது நிலுவையில் உள்ள பணம் ₹{purchase.due_amount}"

            msg += f"\n\n{check_mark} நன்றி! - SK Dresses"

            sms_msg = f"வணக்கம் {customer.name}, \n₹{payment.amount_paid} {payment.payment_type} மூலம் {date} தேதியில் பெற்றோம். நிலுவை பணம் ₹{purchase.due_amount}. நன்றி – SK Dresses."
        else:
            msg = default_no_payment_message(customer.name)
            sms_msg = default_no_payment_message(customer.name)

        share_url = f"https://wa.me/?text={quote_plus(msg)}"

        encoded_msg = quote_plus(sms_msg)

        sms_url = f"sms:{customer.phone}?&body={encoded_msg}"
        
        payment_data.append({
            "customer_name": customer.name,
            "area": customer.area,
            "amount_paid": payment.amount_paid,
            "payment_mode": payment.payment_type,
            "payment_date": date,
            "purchase_id": purchase.id,
            "due_amount": purchase.due_amount,
            "share_url": share_url,
            "sms_url": sms_url
        })
        # For display, store in a dict or use in template:
        # print(f"{customer.name}: {share_url}")
    
    paginator = Paginator(payment_data, 10)  # 10 payments per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'payments_count': payments_count, 'page_obj': page_obj}
    return render(request, 'pages/list_payments.html', context)

def register(request):
    if request.method == 'POST':
        if not User.objects.filter(username=request.POST['username']).exists():
            User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['password'] ,
                                    first_name=request.POST['first_name'], last_name=request.POST['last_name'])
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'User account is already Exists.')
            return redirect('register')
    return render(request, 'accounts/auth-register.html')

# Customer registration view
@login_required
def register_customer(request):
    if request.method == 'POST':
        if Customer.objects.filter(phone= request.POST.get('phone')).exists():
            messages.error(request,'Customer already exists!')
            return redirect('add_customer')
        else:
            Customer.objects.create(
                name=request.POST['name'],
                phone=request.POST['phone'],
                # address_line1=request.POST['address_line1'],
                # address_line2=request.POST.get('address_line2', ''),
                area=request.POST['area'],
                # city=request.POST['city'],
                # pin=request.POST['pin'],
                city = "Chennai", pin = "600077",
                # lat=request.POST.get('lat'),
                # lng=request.POST.get('lng'),
                payment_frequency=request.POST['payment_frequency']

            )
            
            # message = f"Hi {request.POST['name']}, welcome to SK Dresses!"
            # try:
            #     client = get_sns_client()
            #     response = client.publish(
            #         PhoneNumber = request.POST['phone'],
            #         Message=message
            #     )
            #     print("SNS Response:", response)
            # except Exception as e:
            #     print("SNS Error:", e)
            # msg call
            messages.success(request,'New Customer added successfully!')
        return redirect('purchase_product')
    return render(request, 'pages/add_customer.html', {'segment': 'add_customer'})

@login_required
def list_customers(request):
    customers = Customer.objects.all()
    return render(request, 'pages/list_customers.html', {'customers': customers, 'segment': 'list_customers'})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'pages/customer_detail.html', {'customer': customer})

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        # form = CustomerForm(request.POST, instance=customer)
        # if form.is_valid():
        #     form.save()
        Customer.objects.filter(pk = pk).update(
                name=request.POST['name'],
                phone=request.POST['phone'],
                address_line1=request.POST['address_line1'],
                address_line2=request.POST.get('address_line2', ''),
                area=request.POST['area'],
                city=request.POST['city'],
                pin=request.POST['pin'],
                # lat=request.POST.get('lat'),
                # lng=request.POST.get('lng'),
                payment_frequency=request.POST['payment_frequency']
            )
        return redirect('add_customer')
    # else:
    #     form = CustomerForm(instance=customer)
    return render(request, 'pages/customer_edit.html', {'customer': customer})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('list_customers')

# Dress purchase view
@login_required
def purchase_product(request):
    customers = Customer.objects.all()
    if request.method == 'POST':
        print(request.POST)
        customer = get_object_or_404(Customer, id=request.POST['customer'])
        downpayment = float(request.POST.get('downpayment', 0))
        payment_type=request.POST['payment_mode']
        reference_id = request.POST.get('reference_id')
        purchase_date = request.POST.get('purchase_date', None)
        payment_date = request.POST.get('payment_date', None)
        # Add Purchased Items
        purchase = DressPurchase.objects.create(
            customer=customer,
            downpayment=downpayment,
            purchase_date = purchase_date,
            # payment_frequency=request.POST['payment_frequency']
        )
        total_amount = 0
        items = request.POST.getlist('item_name[]')
        quantities = request.POST.getlist('quantity[]')
        prices = request.POST.getlist('unit_price[]')
        for name, qty, price in zip(items, quantities, prices):
            item = PurchaseItem.objects.create(
                purchase=purchase,
                item_name=name,
                quantity=int(qty),
                unit_price=float(price)
            )
            total_amount += item.quantity * item.unit_price
        purchase.total_amount = total_amount
        purchase.save()
        # Add Payment Info
        Payment.objects.create(purchase=purchase, amount_paid=downpayment, payment_type=payment_type, payment_date = payment_date, payment_date_time = payment_date, reference_id=reference_id)
        return redirect('purchase_product')
    return render(request, 'pages/product_purchase.html', {'customers': customers, 'segment': 'product_purchase'})

# Payment entry view
@login_required
def record_payment(request):
    purchases = DressPurchase.objects.select_related('customer').all()

    if request.method == 'POST':
        print(request.POST)
        try:
            purchase = get_object_or_404(DressPurchase, id=request.POST['purchase'])
            Payment.objects.create(
                purchase=purchase,
                amount_paid=request.POST['amount_paid'],
                payment_type=request.POST['payment_mode'],
                collected_by=request.session.get('username',''),
                reference_id=request.session.get('reference_id',''),
                payment_date = request.POST.get('payment_date', None),
                payment_date_time = request.POST.get('payment_date', None)
            )
            messages.success(request,'Payment recorded successfully!')
        except Exception as e:
            print(e)
            messages.error(request,'Payment entry is failed! Try again.')
        return redirect('record_payment')
    # Use a dictionary to store total dues per customer
    customer_dues = defaultdict(int)

    for purchase in purchases:
        customer = purchase.customer
        key = customer.id
        label = f"{customer.name} - {customer.area}"
        customer_dues[key] = {
            'label': label,
            'amount': customer_dues.get(key, {}).get('amount', 0) + (purchase.due_amount or 0)
        }

    # Convert to regular dict if needed
    customer_dues = dict(customer_dues)

    # Filter out zero dues
    customer_dues = {k: v for k, v in customer_dues.items() if v['amount'] > 0}
    return render(request, 'pages/payment_entry.html', {'purchases': purchases, 'customer_dues': customer_dues, 'segment': 'record_payment'})

@login_required
def payment_history(request):
    purchases = DressPurchase.objects.select_related('customer').prefetch_related('payment_set', 'items')
    # Use OrderedDict to preserve order and avoid potential issues
    customer_map = OrderedDict()

    for purchase in purchases:
        customer = purchase.customer
        cust_id = customer.id

        if cust_id not in customer_map:
            customer_map[cust_id] = {
                'customer': customer,
                'items': [],
                'payments': [],
                'total_purchase_amount': 0,
                'total_paid_amount': 0,
                'pending_due_amount': 0,
            }

        # Add purchase totals
        customer_map[cust_id]['total_purchase_amount'] += purchase.total_amount or 0
        customer_map[cust_id]['total_paid_amount'] += purchase.paid_amount or 0
        customer_map[cust_id]['pending_due_amount'] += purchase.due_amount or 0

        # Collect all items, tagging them with their purchase date
        for item in purchase.items.all():
            customer_map[cust_id]['items'].append({
                'item': item,
                'purchase_date': purchase.purchase_date,
            })

        # Collect all payments
        for payment in purchase.payment_set.all():
            customer_map[cust_id]['payments'].append(payment)

    # Now, generate WhatsApp message for each customer
    for data in customer_map.values():
        msg = f"Customer: {data['customer'].name}\nArea: {data['customer'].area}\n"
        msg += f"\nTotal Purchase: ₹{data['total_purchase_amount']}"
        msg += f"\nTotal Paid: ₹{data['total_paid_amount']}"
        msg += f"\nPending Due: ₹{data['pending_due_amount']}"

        msg += "\n\nPurchased Items:"
        for wrapped in data['items']:
            item = wrapped['item']
            date = wrapped['purchase_date'].strftime("%d-%b-%Y")
            msg += f"\n- {item.item_name} x {item.quantity} (₹{item.subtotal}) on {date}"

        msg += "\n\nPayments:"
        for payment in data['payments']:
            date = payment.payment_date.strftime("%d-%b-%Y")
            msg += f"\n- ₹{payment.amount_paid} on {date}"

        # Add encoded share link
        data['whatsapp_share_url'] = f"https://wa.me/?text={quote_plus(msg)}"

    # for cust_id, data in customer_map.items():
    #     print(f"\nCustomer ID: {cust_id}")
    #     print(f"Customer Name: {data['customer'].name}")
    #     print("Purchases:")
    #     for purchase in data['purchases']:
    #         print(f"  - Purchase ID: {purchase.id}, Date: {purchase.purchase_date}, Total: {purchase.total_amount}")
    #         print("    Items:")
    #         for item in purchase.items.all():
    #             print(f"      • {item.item_name} x {item.quantity}")
    #         print("    Payments:")
    #         for payment in purchase.payment_set.all():
    #             print(f"      ₹{payment.amount_paid} on {payment.payment_date}")

    context = {
        'purchases': purchases, 'customer_purchases': list(customer_map.values()), 'segment': 'manage_orders',
    }
    return render(request, 'pages/payment_history.html', context)

# Return or Exchange view
@login_required
def submit_return_exchange(request):
    purchases = DressPurchase.objects.select_related('customer').all()
    if request.method == 'POST':
        purchase = get_object_or_404(DressPurchase, id=request.POST['purchase'])
        ReturnOrExchange.objects.create(
            purchase=purchase,
            request_type=request.POST['request_type'],
            condition_notes=request.POST['condition_notes']
        )
        return redirect('submit_return_exchange')
    return render(request, 'pages/return_exchange.html', {'purchases': purchases})

@login_required
def inventory_list(request):
    inventory_items = InventoryItem.objects.all().order_by('-updated_at')
    context = {'inventory_items': inventory_items, 'segment': 'inventory',}
    return render(request, 'pages/inventory_list.html', context)

@login_required
def add_inventory_item(request):
    if request.method == 'POST':
        print(request.POST)
        print("I'm in Add item")
        InventoryItem.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            hsn_sac_code=request.POST.get('hsn_sac_code'),
            actual_price=request.POST.get('actual_price') or 0,
            markup_price=request.POST.get('markup_price') or 0,
            unit=request.POST.get('unit'),
        )
        messages.success(request,'New Item added inventory successfully!')
        return redirect('inventory_list')
    inventory_items = InventoryItem.objects.all().order_by('-updated_at')
    context = {'inventory_items': inventory_items, 'segment': 'inventory', 'title': 'Add Inventory Item' }
    return render(request, 'pages/add_edit_inventory.html', context)

@login_required
def edit_inventory_item(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)

    if request.method == 'POST':
        print(request.POST)
        print("I'm in Edit")
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.hsn_sac_code = request.POST.get('hsn_sac_code')
        item.actual_price = request.POST.get('actual_price') or 0
        item.markup_price = request.POST.get('markup_price') or 0
        item.unit = request.POST.get('unit')
        item.save()

        messages.success(request,'Modified inventory item successfully!')
        return redirect('inventory_list')
    inventory_items = InventoryItem.objects.all().order_by('-updated_at')
    context = {'inventory_items': inventory_items, 'segment': 'inventory','title': 'Edit Inventory Item' , 'item': item}
    return render(request, 'pages/add_edit_inventory.html', context)

@login_required
def delete_inventory_item(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)

    if item:
        item.delete()
        messages.success(request, "Inventory item deleted successfully.")
        return redirect('inventory_list')

    messages.warning(request, "Invalid request method.")
    return redirect('inventory_list')


def customer_payments_json(request, customer_id):
    payments = Payment.objects.filter(purchase__customer_id=customer_id).order_by('-payment_date_time')
    data = [
        {
            'amount_paid': p.amount_paid,
            'date': p.payment_date_time.strftime('%d-%b-%Y %I:%M %p'),
            'collector': p.collected_by or '—',
        }
        for p in payments
    ]
    return JsonResponse(data, safe=False)

def customer_purchases_json(request, customer_id):
    purchases = PurchaseItem.objects.filter(purchase__customer_id=customer_id).order_by('-purchase__purchase_date')
    data = [
        {
            'name': item.item_name,
            'quantity': item.quantity,
            'unit_price': float(item.unit_price),
            'total_price': float(item.subtotal),
            'date': item.purchase.purchase_date.strftime('%d-%b-%Y'),
        }
        for item in purchases
    ]
    return JsonResponse(data, safe=False)

def create_return_request(request, item_id):
    item = get_object_or_404(PurchaseItem, id=item_id)
    if request.method == 'POST':
        days_since_purchase = (timezone.now().date() - item.purchase_date).days
        if days_since_purchase > 7:
            return HttpResponse("Return period expired.", status=400)

        ReturnRequest.objects.create(
            customer=item.customer,
            purchased_item=item,
            reason=request.POST['reason'],
            photo=request.FILES['photo']
        )
        return redirect('customer_summary')

    return render(request, 'pages/create_return.html', {'item': item})

def admin_review_return(request, return_id):
    r = get_object_or_404(ReturnRequest, id=return_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            r.is_approved = True
            # Logic to adjust balance or issue replacement
        elif action == 'reject':
            r.is_approved = False
        r.save()
        return redirect('return_requests_admin')

    return render(request, 'pages/review_return.html', {'request_obj': r})

def create_exchange_request(request, item_id):
    item = get_object_or_404(PurchaseItem, id=item_id)
    if request.method == 'POST':
        ExchangeRequest.objects.create(
            customer=item.customer,
            purchased_item=item,
            reason=request.POST['reason'],
            checklist_not_washed='not_washed' in request.POST,
            checklist_not_cut='not_cut' in request.POST,
            checklist_ppe_intact='ppe_intact' in request.POST
        )
        return redirect('customer_summary')

    return render(request, 'pages/create_exchange.html', {'item': item})

def admin_review_exchange(request, exchange_id):
    req = get_object_or_404(ExchangeRequest, id=exchange_id)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'approve':
            req.is_approved = True
            replacement_id = request.POST.get('replacement_item')
            if replacement_id:
                req.replacement_item = InventoryItem.objects.get(id=replacement_id)
        elif action == 'reject':
            req.is_approved = False
        req.save()
        return redirect('exchange_requests_admin')

    inventory = InventoryItem.objects.all()
    return render(request, 'pages/review_exchange.html', {'req': req, 'inventory': inventory})
