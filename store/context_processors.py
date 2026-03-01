from .models import Cart


def cart_processor(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = sum(item.quantity for item in cart.items.all())
        return {'cart_items_count': total_items}
    return {'cart_items_count': 0}