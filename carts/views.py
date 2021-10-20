from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from store.models import Product,Variations
from .models import Cart,CartItem
from django.http import request
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.

# def cart(request):
#     return render(request,'store/cart.html')


def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart

def add_cart(request,product_id):
    product=Product.objects.get(id=product_id) #get product
    product_variation=[]

    if request.method=='POST':
        for item in request.POST:
            key=item
            value=request.POST[key]

            try:
                variation=Variations.objects.get(product=product, variation_category__iexact=key,variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

        # color=request.POST['color']
        # size=request.POST['size']
        #return HttpResponse(key+' '+value)
        #
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))

    except Cart.DoesNotExist:
        cart=Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    is_cart_item_exist=CartItem.objects.filter(product=product,cart=cart)
    if is_cart_item_exist:
        cart_item=CartItem.objects.filter(product=product,cart=cart)
        # exisiting variations --db
        # current variation --UI
        # Item_id-- db
# current variation in existing 
        ex_var_list=[]
        id=[]
        for item in cart_item:
            existing_variation=item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)
        
        if product_variation in ex_var_list:
            #increase qunatity
            index=ex_var_list.index(product_variation)
            item=CartItem.objects.get(product=product,id=id[index])
            item.quantity+=1
            item.save()
        else:
            item=CartItem.objects.create(product=product,quantity=1,cart=cart)
            if len(product_variation)>0:
                item.variations.clear()
                item.variations.add(*product_variation)
        # cart_item.quantity+=1
            item.save()
    else :
        item=CartItem.objects.create(product=product,quantity=1,cart=cart,)
        if len(product_variation)>0:
            item.variations.clear()
            item.variations.add(*product_variation)
        item.save()
    # return HttpResponse(cart_item.product)
    # exit() #to check the values getting transitted
    return redirect('cart')

def cart(request,total=0,quantity=0,cart_items=None):
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total+=(cart_item.product.price * cart_item.quantity)
            quantity+=cart_item.quantity
        tax=(2*total)/100
        grand_total=total+ tax
    except ObjectDoesNotExist:
        pass 

    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,

    }


    return render(request,'store/cart.html',context)

def remove_cart(request,product_id,cart_item_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    try:
        cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity>1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

# def remove_cart(request,product_id):
#     cart=Cart.objects.get(cart_id=_cart_id(request))
#     product=get_object_or_404(Product,id=product_id)
#     cart_item=CartItem.objects.get(product=product,cart=cart)
#     if cart_item.quantity>1:
#         cart_item.quantity-=1
#         cart_item.save()
#     else:
#         cart_item.delete()
#     return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')