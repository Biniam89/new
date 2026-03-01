from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json

from .models import Phone, Brand, Comment, PhoneImage, Cart, CartItem
from .forms import PhoneForm, CommentForm


def home(request, brand_id=None):
    search_query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    ram_filter = request.GET.get('ram')

    brands = Brand.objects.all()
    phones = Phone.objects.filter(is_active=True).order_by('-date_added')
    current_brand = None

    if brand_id:
        current_brand = get_object_or_404(Brand, id=brand_id)
        phones = phones.filter(brand=current_brand)
        
    if search_query:
        phones = phones.filter(title__icontains=search_query)

    if min_price:
        phones = phones.filter(price__gte=min_price)
    if max_price:
        phones = phones.filter(price__lte=max_price)
    if ram_filter:
        phones = phones.filter(ram__icontains=ram_filter)

    # prepare top sellers chart data (by price)
    top_sellers = phones.order_by('-price')[:5]
    top_labels = [p.title for p in top_sellers]
    top_values = [float(p.price) for p in top_sellers]

    return render(request, 'store/home.html', {
        'phones': phones,
        'brands': brands,
        'current_brand': current_brand,
        'top_labels_json': json.dumps(top_labels),
        'top_values_json': json.dumps(top_values),
    })


def phone_detail(request, phone_id):
    phone = get_object_or_404(Phone, id=phone_id, is_active=True)
    related = Phone.objects.filter(brand=phone.brand, is_active=True).exclude(id=phone_id)[:4]
    comments = phone.comments.all().order_by('-date_added')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.phone = phone
            if request.user.is_authenticated:
                comment.name = request.user.username
            comment.save()
            return redirect('phone_detail_url', phone_id=phone.id)
    else:
        initial_data = {'name': request.user.username} if request.user.is_authenticated else {}
        form = CommentForm(initial=initial_data)

    return render(request, 'store/phone_detail.html', {
        'phone': phone, 
        'related': related,
        'comments': comments,
        'form': form
    })


@login_required
def custom_admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home_url')
    
    phones = Phone.objects.filter(is_active=True).order_by('-date_added')
    
    if request.method == 'POST':
        form = PhoneForm(request.POST, request.FILES)
        if form.is_valid():
            new_phone = form.save()
            for file in request.FILES.getlist('gallery_images'):
                PhoneImage.objects.create(phone=new_phone, image=file)
            return redirect('custom_admin_dashboard_url')
    else:
        form = PhoneForm()

    return render(request, 'store/custom_admin/dashboard.html', {'phones': phones, 'form': form})


@login_required
def edit_phone(request, phone_id):
    if not request.user.is_staff:
        return redirect('home_url')
    phone = get_object_or_404(Phone, id=phone_id)
    if request.method == 'POST':
        form = PhoneForm(request.POST, request.FILES, instance=phone)
        if form.is_valid():
            form.save()
            return redirect('custom_admin_dashboard_url')
    else:
        form = PhoneForm(instance=phone)
    return render(request, 'store/custom_admin/edit_phone.html', {'form': form, 'phone': phone})


@login_required
def delete_phone(request, phone_id):
    if not request.user.is_staff:
        return redirect('home_url')
    phone = get_object_or_404(Phone, id=phone_id)
    phone.is_active = False
    phone.save()
    return redirect('custom_admin_dashboard_url')


@login_required
def add_to_cart(request, phone_id):
    phone = get_object_or_404(Phone, id=phone_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    quantity_to_add = 1
    if request.method == 'POST':
        try:
            quantity_to_add = int(request.POST.get('quantity', 1))
            if quantity_to_add < 1:
                quantity_to_add = 1
        except (ValueError, TypeError):
            quantity_to_add = 1
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, phone=phone)
    current_qty = cart_item.quantity if not item_created else 0
    available = max(0, phone.stock - current_qty)
    if available <= 0:
        messages.error(request, 'This product is out of stock.')
        return redirect('phone_detail_url', phone_id=phone.id)
    add_amount = min(quantity_to_add, available)
    if not item_created:
        cart_item.quantity += add_amount
    else:
        cart_item.quantity = add_amount
    cart_item.save()
    if add_amount < quantity_to_add:
        messages.warning(request, f'Only {add_amount} items were available and added to your cart.')
    return redirect('cart_view_url')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart_view_url')


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'store/cart.html', {'cart': cart})
