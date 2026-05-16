from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib import messages
from django.db.models import  Count, Avg, Prefetch
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
import json
from datetime import datetime
from .utils.paystack import Paystack
from decimal import Decimal 
from django.contrib.auth.decorators import login_required



def home(request):
   
    categorys = Category.objects.prefetch_related('subcategory').all()
    

    is_featured = Product.objects.filter(is_featured = True)
    top_rated = Product.objects.order_by('-average_rating')[:3]
    is_latest = Product.objects.order_by('-date_added')[:3]
    # top_rated = Product.objects.filter(is _top=True)[:3]
    # is_latest = Product.objects.filter(is_latest=True)[:3]
    best_seller = Product.objects.filter(is_best_seller=True)[:3]\

   
    
    # base navabar cartitems...
    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer, complete=False)
        items = cart.cartitem_set.all()
        cartQuantity = cart.get_total_quantity
        subtotal = cart.get_cart_totals

    else: 
        customer = None
        cookieData = cookieCart(request)
        cart = cookieData['cart']
        items = cookieData['items']
        cartValues =  cookieData['cartValues']
        subtotal = cartValues['get_cart_totals']
        cartQuantity = cartValues['get_total_quantity']
         
   

    print('items', items)
    context = { 'categorys': categorys, 'is_featured':is_featured, 
               'top_rated':top_rated, 'is_latest': is_latest, 
               'best_seller': best_seller,
               'cart':cart, 'items':items, 'cartQuantity':cartQuantity, 'subtotal':subtotal}
    return render(request, 'main.html', context)


def product_detail(request, pk):
    
    # gets invidual product and loads its variations and reviews related fields
    product = get_object_or_404(Product.objects.prefetch_related('variations'), pk=pk)

    # “Get all products whose subcategory is the same as the subcategory of the current product.”“Now remove the product I’m currently viewing from that list.”    
    related_products = Product.objects.filter(subcategory=product.subcategory).exclude(id=product.id)

    # boolean flags for different section of  frontend page 
    is_featured = Product.objects.filter(is_featured = True)[:3]
    top_rated = Product.objects.filter(is_top=True)[:3]
    is_latest = Product.objects.filter(is_latest=True)[:3]
    best_seller = Product.objects.filter(is_best_seller=True)[:3]


    # get the review count
    reviews =  product.reviews.all()
    review_count = reviews.count()

    rate_sum = 0
    average_rating = 0

    if review_count > 0:
        rate_sum =  sum(review.rating for review in reviews)
        average_rating = rate_sum / review_count
    
    product.average_rating = average_rating
    product.save()

    var_type = []
    variations = product.variations.all()
    for var in variations:
        var_type.append(var.variation_type)
        


    # for  review in reviews:
    #     rate_sum += review.rating
    #     average_rating = rate_sum / review_count

    # print("the customer", review.customer, "raating given", review.rating)

    print("var_type", var_type)
    

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        text = request.POST.get('text', "")
        email = request.POST.get('email', "")
        name = request.POST.get('customer', "")
        customer = None

        # next run validation check
        if not text:
            return messages.error( 'Please input text for that required field')
        
    
        if request.user.is_authenticated:
            try:
                customer = request.user.customer
            except Customer.DoesNotExist:
                customer = None

            if Review.objects.filter(product=product, customer=customer).exists():
                messages.error(request, 'You already make a review for this product')
            else:
                review = Review.objects.create(
                product=product,
                customer = customer,
                rating=rating,
                text=text,
                email=email, 
        )    
            return redirect('view', pk=product.id) 
        else:
                return HttpResponse('Please log in to make a review for a product')
            # if Review.objects.filter(product=product, email=email).exists():
            #     messages.error(request, 'You already make a review for this product')
   
            # review = Review.objects.create(
            #     product=product,
            #     name= name,
            #     rating=rating,
            #     text=text,
            #     email=email,)
            # return redirect('view', pk=product.id) 

             



    # database aggregation for computing the total product average. 
    # average_rating = product.reviews.aggregate(agg=Avg('rating'))['agg']
    # product.rating = average_rating or 0
    # product.save()


    # new_percentage_price =product.price * (product.discount_price / 100)


    # print(new_percentage_price)
    # print('avg_rating', avg_rating)
       # base navabar cartitems...
    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer, complete=False)
        items = cart.cartitem_set.all()
        cartQuantity = cart.get_total_quantity

    else:
        cookieData = cookieCart(request)
        cart = cookieData['cart']
        items = cookieData['items']
        cartValues =  cookieData['cartValues']
        cartQuantity = cartValues['get_total_quantity']
        customer = None

    
    context = {'is_featured':is_featured, 'top_rated':top_rated, 
               'is_latest': is_latest, 'best_seller': best_seller,
                'product': product, 'reviews':reviews,"average_rating":average_rating, 
                'review_count':review_count, 'related_products':related_products,
                "var_type":var_type,  'cart':cart, 'items':items, 'cartQuantity':cartQuantity}
    return render(request, 'product.html', context)





def shop(request):
    products = Product.objects.all()
    
    search = request.GET.get('search')
    subcategory = request.GET.get('subcategory')

    if  subcategory == "all":
        products = products.filter(name__icontains=search)
    else:
        if search:
            products = products.filter(name__icontains=search)
        if subcategory:
            products = products.filter(subcategory__id=subcategory)    
    
    is_featured = Product.objects.filter(is_featured = True)[:3]
    
    categorys = Category.objects.prefetch_related(
        Prefetch(
            'subcategory', queryset=SubCategory.objects.annotate(product_count = Count('products'))
        )
    )

  

    # sorting products at different section of the page...
    # orderby = request.GET.get('orderby', "date_added" )
 
    # if orderby == "price_asc":
    #     products = products.order_by('price') 
    # elif orderby == "menu_order":
    #     products = products.order_by('id')
    # else:
    #     products = products.order_by(f'-{orderby}') 

    sort_options = [
        {'price': '-price'},
        {'price-asc': '-price'},
        {'average_rating': '-average_rating'},
        {'date_added': '-date_added'},
        {'is_best_seller': '-total_sales'},
        {'menu_order': '-id'},
    ]

    orderby = request.GET.get('orderby', 'menu_order')
    if orderby in sort_options:
        products = products.order_by(sort_options[orderby])
   
    # if orderby == 'date':
    #     products = products.order_by('-date_added') 
    
    # elif orderby == 'price':
    #     products = products.order_by('price')
    
    # elif orderby == 'price-desc':
    #     products = products.order_by('-price')
    
    # elif orderby == 'rating':
    #     products = products.order_by('-average_rating')

    # elif orderby == 'popularity':
    #     products = products.order_by('-is_best_seller')  

    # else:
    #     products = products.order_by('-id')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        products = products.filter(price__gte=int(min_price))
    if max_price:
        products = products.filter(price__lte=int(max_price))

    
    # size filter 
    size = request.GET.get('size')

    if size:
       products= products.filter(variations__variation_type=size).distinct()


    
    # rendering out cart quantity
    # base navabar cartitems...
    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer, complete=False)
        items = cart.cartitem_set.all()
        cartQuantity = cart.get_total_quantity
    else:
        customer = None
        cookieData = cookieCart(request)
        cartValues =  cookieData['cartValues']
        cartQuantity = cartValues['get_total_quantity']
        cart = cookieData['cart']
        items = cookieData['items'] 
    
    # django pagination
    p = Paginator(Product.objects.all(), 1)
    page = request.GET.get('page') 
    products = p.get_page(page)
    # nums = "a" * products.paginator.num_pages

    # page range for pagination... 
    current_page = products.number
    total_pages = p.num_pages
    page_range =  range(max(current_page-2,1), min(current_page+3, total_pages+1))
    
    context = {'products':products, 'is_featured':is_featured, 
               'categorys':categorys, 'page_range':page_range,
                 'total_pages':total_pages, 'cart':cart, 'items':items, 'cartQuantity':cartQuantity}
    return render(request, 'shop.html', context)


    # old checkout
# def checkout(request):

#     if not request.user.is_authenticated:
#         return HttpResponse('Please log in...')
    
#     total = 0
#     shipping_cost = 0
#     transaction_id = datetime.now().timestamp()
#     shipping_type = 'pickup'

    
   
#     if request.user.is_authenticated:
       
#         customer = request.user.customer
#         cart, created = Cart.objects.get_or_create(customer=customer, complete=False)
#         items = cart.cartitem_set.all()

#         shipping = ShippingFee.objects.all()    
#         cart_total = cart.get_cart_totals

#         if request.method == 'POST':
#             # Billing info
#             first_name = request.POST.get("first_name")
#             last_name = request.POST.get("last_name")
#             email = request.POST.get("email")
#             phone = request.POST.get("phone")

#             address = request.POST.get("address")
#             city = request.POST.get("city")
#             state = request.POST.get("state")
#             zipcode = request.POST.get("zipcode")

#             shipping_type = request.POST.get("shipping_type", 'pickup')

           

#             if shipping_type ==  "delivery":
#                 if state:
#                     shipping_list = ShippingFee.objects.filter(state=state).first()
#                     if shipping_list:
#                       shipping_cost = shipping_list.fee 
#                     else:
#                         shipping_cost = 0
#             else:
#                 shipping_cost = 0
#             total = cart_total + shipping_cost

#             # # 🔹 3. INITIALIZE PAYSTACK
#             # payment_data = Paystack.initialize_payment(email, total)

#             # if not payment_data.get("status"):
#             #     return redirect("checkout")

#             # # 🔹 4. GET PAYSTACK DATA
#             # reference = payment_data["data"]["reference"]
#             # payment_url = payment_data["data"]["authorization_url"]


#             #   CREATE PENDING ORDER
#             order = Order.objects.create(
#                 customer=customer,
#                 shipping_type = shipping_type,  
#                 # transaction_id = reference,
#                 complete = False, 
#                 total = total, 


#             )

#             #  CREATE ORDER ITEMS FROM CARTITEMS
#             for item in items:
#                 OrderItem.objects.create(
#                     order=order,
#                     product=item.product,
#                     quantity=item.quantity,
#                     price=item.product.price
#                 )

#             #  CREATE SHIPPING ADDRESS (ONLY IF DELIVERY)
#             if shipping_type == "delivery":
#                 ShippingAddress.objects.create(
#                     customer=customer,
#                     order=order,
#                     address=address,
#                     city=city,
#                     state=state,
#                     zipcode=zipcode,
#                     first_name = first_name, 
#                     last_name= last_name, 
#                     email = email, 
#                     phone = phone
#                 )

        
#              # ❗ DO NOT CLEAR CART YET

#             # 🔹 8. REDIRECT TO PAYSTACK
#             # return redirect(payment_url)
     
#     else:
#         pass
   
#     print("Shipping Type:", request.POST)
    
#     context = {
#         'items':items, 
#         'cart':cart, 
#         'shipping':shipping,
#         'total': total 
#     }
#     return render(request, 'checkout.html', context)

# new checkout with ajax shipping fee calculation
def checkout(request):

    if not request.user.is_authenticated:
        return HttpResponse('Please log in...')

    customer = request.user.customer
    cart, created = Cart.objects.get_or_create(customer=customer, complete=False)
    items = cart.cartitem_set.all()

    shipping_list = ShippingFee.objects.all()
    cart_total = cart.get_cart_totals

    shipping_cost = 0
    shipping_type = 'pickup'

    if request.method == 'POST':
   
        shipping_type = request.POST.get("shipping_type", 'pickup')
        state = request.POST.get("state")

        if shipping_type == "delivery":
            shipping = ShippingFee.objects.filter(state=state).first()
            if shipping:
                shipping_cost = shipping.fee
            else:
                shipping_cost = 0

        
        else:
            shipping_cost = 0
        
    total = cart_total + shipping_cost

    context = {
        'items': items,
        'cart': cart,
        'shipping': shipping_list,
        'cart_total': cart_total,
        'shipping_cost': shipping_cost,
        'total': total,
        'shipping_type': shipping_type,
    }

    return render(request, 'checkout.html', context)


def cart(request):
    
    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer, complete=False)
        items = cart.cartitem_set.all()
        cartQuantity =  cart.get_total_quantity
        subtotal =  cart.get_cart_totals
    else:
        cookieData = cookieCart(request)
        cart = cookieData['cart']
        items = cookieData['items']
        cartValues =  cookieData['cartValues']
        subtotal = cartValues['get_cart_totals']
        cartQuantity = cartValues['get_total_quantity']
    

    # calculating shipping cost
    # shipping_cost = 2000
    # total = shipping_cost + cart.get_cart_totals
    
    shipppingFee = ShippingFee.objects.all()

    shipping_type = request.GET.get('shipping_type', 'pickup')

    
    state = request.GET.get('state')  # from user input
    city = request.GET.get('city')
    zipcode = request.GET.get('zipcode')

    shipping_cost = 0

    if shipping_type == 'pickup':
        shipping_cost = 0 

    elif shipping_type == 'delivery':
        if state:
            shipping = ShippingFee.objects.filter(state=state).first()
            if shipping:  
                shipping_cost = shipping.fee

    if request.user.is_authenticated:
        total = cart.get_cart_totals + shipping_cost
    else:
        total = cartValues['get_cart_totals'] + shipping_cost

    print('total', items)
    return render(request, 'cart.html', {
        'items':items,
        'cart':cart,
        'total':total,
        'shipppingFee':shipppingFee, 
        'cartQuantity':cartQuantity, 
        'subtotal':subtotal
    })


# AJAX to update Item in cart 
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    # get the customer
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    cart, created = Cart.objects.get_or_create(customer=customer, complete=False)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if action == 'add':
        item.quantity = item.quantity+1
    elif action == 'remove':
        item.quantity = item.quantity-1
    item.save()

    if item.quantity <=0:
        item.delete()
   
    return JsonResponse('Item was added successfully', safe=False)


def removeItem(request):
    data = json.loads(request.body)
    itemId = data['itemId']

    item = CartItem.objects.get(id=itemId)
    item.delete()

    print('itemId', itemId)
    return JsonResponse('Succes', safe=False)


# def removeItem(request, pk):
#     item = get_object_or_404(CartItem, pk=pk)
#     # item = CartItem.objects.get(id=pk)
#     item.delete()

#     return  redirect('cart')




def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')

def loginPage(request):
    return render(request, 'login.html')


def forgot(request):
    return render(request, 'forgot-password.html')


def wishlistt(request):
    return render(request, 'wishlist.html')



def single (request):
    return render(request, 'single.html')

def category(request):
    return render(request, 'category.html')


def blog(request):
    return render(request, 'blog.html')



def get_shipping_fee(request):
    state = request.GET.get('state')

    shipping = ShippingFee.objects.filter(state=state).first()

    if shipping:
        fee = float(shipping.fee)
    else:
        fee = 0   # ✅ important fallback

    return JsonResponse({'fee': fee})


def cookieCart(request):
    try:
        cart = json.loads( request.COOKIES['cart'])
    except:
        cart = {}
    items  = []
    
    cartValues = {'get_cart_totals': 0, 'get_total_quantity': 0}
    subtotal = 0
    

    for i in cart:
        try:
            # getting and displaying the total quantitites....
            quantity = cart[i]['quantity']
            # getting product...
            product = Product.objects.get(id=i)
            # getting subtotal for eachh item 
            subtotal = product.price * cart[i]['quantity']

            cartValues['get_cart_totals'] += subtotal
            cartValues['get_total_quantity'] += quantity

            item = {
                'product': {
                    'id': product.id, 
                    'price': product.price, 
                    'imageURL': product.imageURL, 
                    'name':product.name,
                }, 
                'quantity': cart[i]['quantity'], 
                'get_subtotal': subtotal
            }

            items.append(item)
        except:
            pass

    return  {'cart': cart,  
             'items': items, 'cartValues':cartValues, 'subtotal':subtotal
             } 


# intialize payment view with ajax and create order before redirecting to paystack
def initialize_payment_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zipcode = request.POST.get("zipcode")

        customer = request.user.customer
        cart = Cart.objects.get(customer=customer, complete=False)
        items = cart.cartitem_set.all()

        # ✅ Calculate amount from backend
        cart_total = cart.get_cart_totals

        shipping_type = request.POST.get("shipping_type")
        state = request.POST.get("state")

        shipping_cost = 0

        if shipping_type == "delivery":
            shipping = ShippingFee.objects.filter(state=state).first()
            if shipping:
                shipping_cost = shipping.fee

            

        total = cart_total + shipping_cost

        # ✅ Create Order
        order = Order.objects.create(
            customer=customer,
            total=total,
            complete=False
        )

        # ✅ Create Order Items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        if shipping_type == "delivery":
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=address,
                city=city,
                state=state,
                zipcode=zipcode,
                first_name = first_name, 
                last_name= last_name, 
                email = email, 
                phone = phone
        )
        # ✅ Initialize Paystack
        response = Paystack.initialize_payment(customer.user.email, total)

        if response.get("status"):
            payment_url = response["data"]["authorization_url"]
            reference = response["data"]["reference"]

            order.transaction_id = reference
            order.save()

            # ✅ RETURN JSON (for AJAX)
            return JsonResponse({
                "status": True,
                "payment_url": payment_url
            })
        

        return JsonResponse({"status": False})


def verify_payment(request):

    reference = request.GET.get("reference")

    if not reference:
        return redirect("checkout")

    response = Paystack.verify_payment(reference)

    if response.get("status") and response["data"]["status"] == "success":

        order = Order.objects.get(transaction_id=reference)

        # prevent double payment
        if order.complete:
            return redirect("success")

        order.complete = True
        order.save()

        # 🔥 NOW clear cart
        cart = Cart.objects.get(customer=order.customer, complete=False)
        cart.complete = True
        cart.save()

        return redirect("success")

    return redirect("checkout")


def success_page(request):
    return render(request, "success.html")



