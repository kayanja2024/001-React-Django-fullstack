from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Product, Cart, CartItem, Transaction
from .serializers import ProductSerializer, DetailedProductSerializer, CartItemSerializer
from .serializers import  SimpleCartSerializer, CartSerializer, UserSerializer, UserSignupSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.http import JsonResponse
import logging
from decimal import Decimal
import uuid
from django.conf import settings
import requests
from django.contrib.auth.decorators import login_required
from .models import Cart, Transaction
import paypalrestsdk
import json
import os
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

BASE_URL = settings.REACT_BASE_URL


# @api_view(['POST'])
# def signup(request):
#     if request.method == 'POST':
#         serializer = UserSignupSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





User = get_user_model()

@csrf_exempt
@api_view(["POST"])
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            firstname = data.get('firstname', '').strip()
            lastname = data.get('lastname', '').strip()
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            password2 = data.get('password2', '')

            if not all([firstname, lastname, username, email, password, password2]):
                return JsonResponse({'detail': 'All fields are required.'}, status=400)
            if password != password2:
                return JsonResponse({'detail': 'Passwords do not match.'}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'detail': 'Username already taken.'}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'detail': 'Email already in use.'}, status=400)

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=firstname,
                last_name=lastname
            )
            user.save()

            return JsonResponse({'message': 'User created successfully.'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'detail': str(e)}, status=500)

    return JsonResponse({'detail': 'Method not allowed.'}, status=405)




paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

@api_view(["GET"])
def products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)



@api_view(["GET"])
def product_detail(request, slug):
    product = Product.objects.filter(slug=slug).first()  # Get the first product with this slug
    if not product:
        return Response({"error": "Product not found"}, status=404)

    serializer = DetailedProductSerializer(product)  # Pass a single product instance
    return Response(serializer.data)


@api_view(["POST"])
def add_item(request):
    try:
        cart_code = request.data.get("cart_code")
        product_id = request.data.get("product_id")

        cart, created = Cart.objects.get_or_create(cart_code=cart_code)
        product = Product.objects.get(id=product_id)

        cartitem, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cartitem.quantity = 1
        cartitem.save()

        serializer = CartItemSerializer(cartitem)
        return Response({"datat": serializer.data, "message": "cartitem created succesifuly"}, status=201)
    except Exception  as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
def product_in_cart(request):
    cart_code = request.query_params.get("cart_code")
    product_id = request.query_params.get("product_id")

    cart = Cart.objects.get(cart_code=cart_code)
    product = Product.objects.get(id=product_id)

    product_exists_in_cart = CartItem.objects.filter(cart=cart, product=product).exists()

    return Response({"product_in_cart": product_exists_in_cart},)



@api_view(["GET"])
def get_cart_stat(request):
    cart_code = request.query_params.get("cart_code")
    cart = Cart.objects.get(cart_code=cart_code, paid=False)
    serializer = SimpleCartSerializer(cart)
    return Response(serializer.data)



# @api_view(['GET'])
# def get_cart_stat(request):
#     cart_code = request.GET.get("cart_code")

#     if not cart_code:
#         return Response({"error": "Cart code is required"}, status=400)

#     cart = Cart.objects.filter(cart_code=cart_code, paid=False).first()

#     if cart is None:
#         return Response({"error": "Cart not found"}, status=404)

#     return Response({"cart_code": cart.cart_code, "total_items": cart.total_items})



# logger = logging.getLogger(__name__)

# def get_cart_stat(request):
#     cart_code = request.GET.get('cart_code')
#     if not cart_code:
#         return JsonResponse({'error': 'No cart_code provided'}, status=400)

#     try:
#         # Check if cart exists with the given cart_code and that it's not paid
#         cart = Cart.objects.get(cart_code=cart_code, paid=False)
#         return JsonResponse({
#             'id': cart.id,
#             'cart_code': cart.cart_code,
#             'items': cart.items,  # Make sure this field exists in your model
#             'sum_total': cart.sum_total,
#             'num_of_items': cart.num_of_items,
#         })
#     except Cart.DoesNotExist:
#         logger.error(f"Cart with code {cart_code} does not exist.")
#         return JsonResponse({'error': 'Cart not found'}, status=404)
#     except Exception as e:
#         logger.error(f"Error occurred while fetching cart data: {str(e)}")
#         return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)


@api_view(["GET"])
def get_cart(request):
    cart_code = request.query_params.get("cart_code")
    cart = Cart.objects.get(cart_code=cart_code, paid=False)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(["PATCH"])
def update_quantity(request):
    try:
        cartitem_id = request.data.get("item_id")
        quantity = request.data.get("quantity")
        quantity = int(quantity)
        cartitem = CartItem.objects.get(id=cartitem_id)
        cartitem.quantity = quantity
        cartitem.save()
        serializer = CartItemSerializer(cartitem)
        return Response({"data": serializer.data, "message": "Cartitem updated successifully!"})
    except Exception as e:
        return Response({'err': str(e)}, status=400)
    

# @api_view(["POST"])
# def delete_cartitem(request):
#     cartitem_id = request.data.get("item_id")
#     cartitem = CartItem.objects.get(id=cartitem_id)
#     cartitem.delete()
#     return Response({"message": "item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def delete_cartitem(request):
    cartitem_id = request.data.get("item_id")  # Ensure correct key is used
    
    if not cartitem_id:
        return Response({"error": "item_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cartitem = CartItem.objects.get(id=cartitem_id)
        cartitem.delete()
        return Response({"message": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except CartItem.DoesNotExist:
        return Response({"error": "CartItem not found"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(["GET"])
# @permission_classes([IsAuthenticated])
# @login_required
def get_username(request):
    user = request.user
    return Response({"username": user.username})


# @api_view(["GET"])
# # @permission_classes([IsAuthenticated])
# def user_info(request):
#     user = request.user
#     serializer = UserSerializer(user)
#     return Response(serializer.data)



@api_view(["GET"])
def user_info(request):
    # Ensure user is authenticated, or return a default response for anonymous users
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
    else:
        return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.data)


# @permission_classes([IsAuthenticated])
# @api_view(["POST"])
# def initiate_payment(request):
#     if request.user:
#         try:
#             # generate a unique transaction reference
#             tx_ref = str(uuid.uuid4())
#             cart_code = request.data.get("cart_code")
#             cart = Cart.objects.get(cart_code=cart_code)
#             user = request.user

#             amount = sum([item.quantity * item.product.price for item in cart.items.all()])
#             tax = Decimal("4.00")
#             total_amount = amount + tax
#             currency = "USD"
#             redirect_url = f"{BASE_URL}/payment-status/"

#             transaction = Transaction.objects.create(
#                 ref=tx_ref,
#                 cart=cart,
#                 amount=total_amount,
#                 currency=currency,
#                 user=user,
#                 status='pending'
#             )

#             flutterwave_payload = {
#                 "tx_ref": tx_ref,
#                 "amount": str(total_amount), #convert to string
#                 "currency": currency,
#                 "redirect_url": redirect_url,
#                 "customer": {
#                     "email": user.email,
#                     "name": user.username,
#                     "phonenumber": user.phone
#                 },
#                 "customizations": {
#                     "title": "shopit payment"
#                 }
#             }

#             # set up the headers for the request

#             headers = {
#                 "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
#                 "Content-Type": "application/json"
#             }

#             # make the API request to Flutterwave

#             Response = requests.post(
#                 'https://api.flutterwave.com/v3/payments',
#                 json = flutterwave_payload,
#                 headers=headers
#             )

#             # check if our request is successful
#             if Response.status_code == 200:
#                 return Response(Response.json(), status=status.HTTP_200_OK)
#             else:
#                 return Response(Response.json(), status=status.HTTP_200_OK)

#         except requests.exceptions.RequestException as e:
#         # log the error and return an error Response
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(["POST"])
def initiate_payment(request):
    if request.user.is_authenticated:  # Check if the user is authenticated
        try:
            # Generate a unique transaction reference
            tx_ref = str(uuid.uuid4())
            cart_code = request.data.get("cart_code")  # Get the cart code from the request
            cart = Cart.objects.get(cart_code=cart_code)  # Fetch the cart using cart_code
            user = request.user

            # Calculate the total amount by summing the item prices in the cart
            amount = sum([item.quantity * item.product.price for item in cart.items.all()])
            tax = Decimal("4.00")  # Static tax amount (can be dynamic if needed)
            total_amount = amount + tax  # Total amount including tax
            currency = "UGX"  # Currency for the payment
            
            redirect_url = f"{settings.BASE_URL}/payment_callback/"  # Using settings for BASE_URL

            # Create a transaction entry in the database
            transaction = Transaction.objects.create(
                ref=tx_ref,
                cart=cart,
                amount=total_amount,
                currency=currency,
                user=user,
                status='pending'
            )

            # Prepare the payload for Flutterwave
            #flutterwave_payload = {
                # "tx_ref": tx_ref,
                # "amount": str(total_amount),  # Convert total amount to string as required by the API
                # "currency": currency,
                # "redirect_url": redirect_url,
                # "customer": {
                #     "email": user.email,
                #     "name": user.username,
                #     "phonenumber": user.phone if user.phone else ""  # Handle the case if the phone number is not provided
                # },
                # "customization": {
                #     "title": "shopit payment"
                # }
            #}

            flutterwave_payload = {
                "tx_ref": tx_ref,
                "amount": str(total_amount),  # Convert total amount to string as required by the API
                "currency": currency,
                "redirect_url": redirect_url,
                "customer": {
                    "email": user.email if user.email else "user@example.com",  # Fallback email
                    "name": user.username,
                    "phonenumber": user.phone if user.phone else ""  # Optional fallback
                },
                "customization": {
                    "title": "shopit payment"
                }
                
            }


            # Set up headers for the Flutterwave API request
            headers = {
                "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
                "Content-Type": "application/json"
            }

            # Make the API request to Flutterwave
            response = requests.post(
                # 'https://api.flutterwave.com/v3/payments',
                'https://api.flutterwave.com/v3/payments',
                json=flutterwave_payload,
                headers=headers
            )

            # Check if our request to Flutterwave is successful
            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)  # Return 400 for failure

        except requests.exceptions.RequestException as e:
            # Handle any request exceptions and return an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Cart.DoesNotExist:
            # Handle the case where the cart is not found in the database
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)  # Return 401 if the user is not authenticated


# @api_view(["GET"])
# def payment_callback(request):
#     status = request.GET.get("status")
#     tx_ref = request.GET.get("tx_ref")
#     transaction_id = request.GET.get("transaction_id")

#     user = request.user

#     if status == "successful":
#         # verifying the Transaction using the fluttervave's api
#         headers = {
#             "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"
#         }

#         response = requests.get(f"https://api.flutterwave.com/v3/transactions/verify", headers=headers)
#         response_data = response.json()

#         if response_data["status"] == "success":
#             transaction = Transaction.objects.get(ref=tx_ref)

#             # confirm the transaction details
#             if (response_data["data"]["status"] == "successful"
#                     and float(response_data["data"]["amount"]) == float(transaction.amount)
#                     and response_data["data"]["currency"] == transaction.currency):

#                 # update transaction and cart status to paid
#                 transaction.status = "completed"
#                 transaction.save()

#                 cart = transaction.cart
#                 cart.paid = True
#                 cart.user = user
#                 cart.save()

#                 return Response({"message": "Payment successful!", "subMessage": "You have successfully made payment"})
#             else:
#                 # payment verification failed
#                 return Response({"message": "payment verification failed.", "subMessage": "your payment verification failed"})
#         else:
#             return Response({"message": "failed to verify payment with flutterwave.", "subMessage": "we couldn't verify your payment"})
#     else:
#         # payment was not successful
#         return Response({"message": "payment was not successful."}, status=400)




# @api_view(['GET', 'POST'])
# def payment_callback(request):
#     status_param = request.GET.get('status')
#     tx_ref = request.GET.get('tx_ref')
#     transaction_id = request.GET.get('transaction_id')

#     headers = {

#         "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",  # Replace with your actual secret key
#         "Content-Type": "application/json"
# }

#     # Replace with the actual URL you're calling (e.g., Flutterwave, Paystack, etc.)
#     verify_url = f"https://api.flutterwave.com/v3/transactions/verify/{transaction_id}"
#     response = requests.get(verify_url, headers=headers)
#     try:
#         response = requests.get(verify_url)

#         # Check if the response is empty
#         if not response.content:
#             return Response({"error": "Empty response from payment gateway."}, status=status.HTTP_502_BAD_GATEWAY)

#         try:
#             response_data = response.json()
#         except json.JSONDecodeError:
#             return Response({"error": "Invalid JSON response from payment gateway."}, status=status.HTTP_502_BAD_GATEWAY)

#         # Continue processing the valid response_data
#         return Response({
#             "message": "Payment callback handled successfully.",
#             "status": status_param,
#             "tx_ref": tx_ref,
#             "transaction_id": transaction_id,
#             "payment_data": response_data,
#         })

#     except requests.RequestException as e:
#         return Response({"error": f"Request failed: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






FLUTTERWAVE_SECRET_KEY = os.getenv("FLUTTERWAVE_SECRET_KEY")  # Or from settings if you're using Django settings
@api_view(['GET', 'POST'])
def payment_callback(request):
    transaction_id = request.GET.get('transaction_id')
    tx_ref = request.GET.get('tx_ref')
    status = request.GET.get('status')

    #Verify payment
    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    response = requests.get(url, headers=headers)

    try:
        response_data = response.json()
    except ValueError:
        response_data = {
            "status": "error",
            "message": "Could not parse JSON from Flutterwave",
            "raw": response.text
        }

    return Response({
        "message": "Payment callback handled successfully.",
        "status": status,
        "tx_ref": tx_ref,
        "transaction_id": transaction_id,
        "payment_data": response_data
    })





@api_view(["POST"])
def initiate_paypal_payment(request):
    if request.method == 'POST' and request.user.is_authenticated:
        # fetch the cart and calculate the total amount
        tx_ref = str(uuid.uuid4())
        user = request.user
        cart_code = request.data.get("cart_code")
        cart = Cart.objects.get(cart_code=cart_code)
        amount = sum(item.product.price * item.quantity for item in cart.items.all())
        tax = Decimal("4.00")
        total_amount = amount + tax

        # create a paypal payment object

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls":{
                # use a single redirect url for both success and cancel 
               "return_url": f"{BASE_URL}/payment-status?paymentStatus=success&ref={tx_ref}",
               "success_url": f"{BASE_URL}/payment-status?paymentStatus=cancel"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Cart items",
                        "sku": "cart",
                        "price": str(total_amount),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(total_amount),
                    "currency": "USD",
                },
                "description": "Payment for cart items"
            }]

        })

        print("pay_id", payment)

        transaction, created = Transaction.objects.get_or_create(
            ref=tx_ref,
            cart=cart,
            amount=total_amount,
            user=user,
            status='pending',
        )

        if payment.create():
            print (payment.links)
            # Extract PayPal approval URL to redirect the user
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)
                    return Response({"approval_url": approval_url})
        else:
            return Response({"error": payment.error}, status=400)
    return Response({"error": "Invalid request"}, status=400)


@api_view(["POST"])
def paypal_payment_callback(request):
    payment_id = request.query_params.get("paymentid")
    payer_id = request.query_params.get("PayerID")
    ref = request.query.params.get("ref")

    user = request.user

    print("refff", ref)

    transaction = Transaction.objects.get(ref=ref)

    if payment_id and payer_id:
        # Fetch payment objects using Paypal SDK
        payment = paypalrestsdk.Payment.find(payment_id)

        transaction.status = "completed"
        transaction.save()

        cart = transaction.cart
        cart.paid = True
        cart.user = user
        cart.save()

        return Response({"message": "payment successful!", "subMessage": "you have successfully made payment for the items you purchased"})
    
    else:
        return Response({"error": "Invalid payment details."}, status=400)
