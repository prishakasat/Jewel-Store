import django
from django.http import HttpResponse, HttpResponseBadRequest
import datetime
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product, Wishlist, NewsLetterUser
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm, FeedbackForm, NewsLetterUserForm, NewsletterForm
from django.core.mail import send_mail
from .models import Newsletter
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required,  user_passes_test
from django.utils.decorators import method_decorator # for Class Based Views
from django.views.decorators.csrf import csrf_exempt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import razorpay
from django.conf import settings

# Create your views here.
def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/index.html', context)


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    context = {
        'product': product,
        'related_products': related_products,

    }
    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})

def contact(request):
    return render(request, 'store/contact.html')

def return_policy(request):
    return render(request, 'store/return.html')

def termCondition(request):
    return render(request, 'store/termsCondition.html')

def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store:home')  # Redirect to home page after successful submission
    else:
        form = FeedbackForm()
    return render(request, 'store/feedback.html', {'form': form})

def newsletterUser(request):
    if request.method == 'POST':
        form = NewsLetterUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store:home')
    else:
        form = NewsLetterUserForm()
    return redirect('store:home')

@user_passes_test(lambda u: u.is_staff)  # Requires user to be staff/admin
def send_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            content = form.cleaned_data['content']
            users = NewsLetterUser.objects.all()
            receiver = []
            for user in users:
                msg = MIMEMultipart()
                msg['From'] = settings.EMAIL_HOST_USER
                msg['To'] = user.email
                msg['Subject'] = subject
                html_content = content
                msg.attach(MIMEText(html_content, 'html'))
                mail = smtplib.SMTP('smtp.gmail.com', 587)
                mail.ehlo()
                mail.starttls()
                mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                mail.sendmail(msg['From'], msg['To'], msg.as_string())
                mail.close()
                receiver.append(user.email)

                # send_mail(subject, content, 'your@email.com', [user.email])
            Newsletter.objects.create(subject=subject, content=content, receiver=receiver)
            return render(request, 'store/newsletter_sent.html')
    else:
        form = NewsletterForm()
    return render(request, 'store/send_newsletter.html', {'form': form})

def logout(request):
    response = HttpResponse("Logout Successfully.")
    response.set_cookie('csrftoken', '', max_age=0)
    response.set_cookie('sessionid', '', max_age=0)
    response = redirect('store:login')
    # Set cookies on the response
    response.set_cookie('csrftoken', '', max_age=0)
    response.set_cookie('sessionid', '', max_age=0)
    return response


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True)
    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/category_products.html', context)


# Authentication Starts Here

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()

        return render(request, 'account/register.html', {'form': form})

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()
    
    return redirect('store:cart')

@login_required
def add_to_wishlist(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Wishlist.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Wishlist, product=product_id, user=user)
        cp.save()
    else:
        Wishlist(user=user, product=product).save()
    
    return redirect('store:wishlist')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount
    if amount >= 500:
        shipping_amount = 0
    else:
        shipping_amount = round(amount * decimal.Decimal(0.1), 2)
    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)

@login_required
def wishlist(request):
    user = request.user
    wishlist_products = Wishlist.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Wishlist.objects.all() if p.user==user]

    context = {
        'wishlist_products': wishlist_products,
        'amount': amount,
    }
    return render(request, 'store/wishlist.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')

@login_required
def remove_wishlist(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Wishlist, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Wishlist.")
    return redirect('store:wishlist')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')

@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')


@login_required
def checkout(request):
    user = request.user
    address = request.GET.get('address')
    submit = request.GET.get('submit')
    request.session['address'] = address
    if submit == "COD":
        cart = Cart.objects.filter(user=user)
        for c in cart:
            # Saving all the products from Cart to Order
            Order(user=user, address=address, product=c.product, quantity=c.quantity, payment_id="COD").save()
            # And Deleting from Cart
            c.delete()
        return redirect('store:orders')
    return redirect('store:payment')


@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})

def test(request):
    return render(request, 'store/test.html')



def calculateAmount(request):
    user = request.user
    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount
    if amount >= 500:
        shipping_amount = 0
    else:
        shipping_amount = round(amount * decimal.Decimal(0.1), 2)
    return decimal.Decimal(amount + shipping_amount)

razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def payment(request):
    currency = 'INR'
    amount = calculateAmount(request) * 100
    amount = int(amount)
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler/'
 
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZORPAY_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
 
    return render(request, 'payment.html', context=context)

@csrf_exempt
def paymenthandler(request):
    user = request.user
    address = request.session.get('address')
    payment_id = request.POST.get('razorpay_payment_id', '')
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(user=user, address=address, product=c.product, quantity=c.quantity, payment_id=payment_id).save()
        # And Deleting from Cart
        c.delete()
    return redirect('store:orders')
    # only accept POST request.
    if request.method == "POST":
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            
            if result is not None:
                amount = calculateAmount(request) * 100
                try:
                    # capture the payment
                    razorpay_client.payment.capture(payment_id, amount)
                    user = request.user
                    address = request.session.get('address')
                    cart = Cart.objects.filter(user=user)
                    for c in cart:
                        # Saving all the products from Cart to Order
                        Order(user=user, address=address, product=c.product, quantity=c.quantity, payment_id=payment_id).save()
                        # And Deleting from Cart
                        c.delete()
                    return redirect('store:orders')
                    # render success page on successful capture of payment
                except Exception as e:
                    # if there is an error while capturing payment.
                    print(e)  # Log the error for debugging purposes
                    return render(request, 'paymentfail.html', context={})
            else:
                # if signature verification fails.
                return render(request, 'paymentfail.html', context={})
        except Exception as e:
            # if we don't find the required parameters in POST data
            print(e)  # Log the error for debugging purposes
            return HttpResponseBadRequest()
    else:
        # if other than POST request is made.
        return HttpResponseBadRequest()