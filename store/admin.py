from django.contrib import admin
from .models import Address, Category, Product, Cart, Order, Wishlist, Feedback, NewsLetterUser, Newsletter

# Register your models here.
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'locality', 'city', 'state')
    list_filter = ('city', 'state')
    list_per_page = 10
    search_fields = ('locality', 'city', 'state')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category_image', 'is_active', 'is_featured', 'updated_at')
    list_editable = ('slug', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured')
    list_per_page = 10
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title", )}


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category', 'product_image', 'is_active', 'is_featured', 'updated_at')
    list_editable = ('slug', 'category', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured')
    list_per_page = 10
    search_fields = ('title', 'category', 'short_description')
    prepopulated_fields = {"slug": ("title", )}

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    list_editable = ('quantity',)
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('user', 'product')
    
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('user', 'product')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'address', 'status', 'ordered_date', 'payment_id', 'tracking_link')
    list_editable = ('quantity', 'status', 'tracking_link')
    list_filter = ('status', 'ordered_date')
    list_per_page = 20
    search_fields = ('user', 'product')

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'product_id', 'product_name', 'message', 'created_at')
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('name', 'email')

class NewsLetterUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('email', )

class NewsLetterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'content', 'receiver', 'created_at')
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('subject', )



admin.site.register(Address, AddressAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(NewsLetterUser, NewsLetterUserAdmin)
admin.site.register(Newsletter, NewsLetterAdmin)