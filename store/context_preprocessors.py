from .models import Category, Cart, Wishlist


def store_menu(request):
    categories = Category.objects.filter(is_active=True)
    context = {
        'categories_menu': categories,
    }
    return context

def cart_menu(request):
    if request.user.is_authenticated:
        cart_items= Cart.objects.filter(user=request.user)
        context = {
            'cart_items': cart_items,
        }
    else:
        context = {}
    return context
def wishlist_menu(request):
    if request.user.is_authenticated:
        wishlist_items= Wishlist.objects.filter(user=request.user)
        context = {
            'wishlist_items': wishlist_items,
        }
    else:
        context = {}
    return context