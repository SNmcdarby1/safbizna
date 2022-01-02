from django.urls import path
from . import views
from .webhooks import webhook

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('checkout_success/<order_number>', views.checkout_success, name='checkout_success'),
    path('cache_checkout_data/', views.cache_checkout_data, name='cache_checkout_data'),
    path('wh/', webhook, name='webhook'),
]

from django.http import JsonResponse

def payment_process(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, ordered=False, id=body['orderID'])

    # create the payment
    payment = Payment()
    payment.stripe_charge_id = body['payID']
    payment.user = request.user
    payment.amount = order.get_total()
    payment.save()

    # assign the payment to the order
    order_items = order.items.all()
    order_items.update(ordered=True)
    for item in order_items:
        item.save()

    order.ordered = True
    order.payment = payment
    order.save()

    # your other logic goes here

    return JsonResponse('Payment submitted..', safe=False)

def order_complete(request):
    messages.success(request, "Your order was successful!")
    return render(request, 'order_complete.html') # you can pass any context as needed