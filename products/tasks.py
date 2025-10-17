from celery import shared_task
from django.core.mail import send_mail
import pandas as pd
from io import BytesIO
from django.db import transaction
from decimal import Decimal

from .models import Product, Order, OrderItem, Customer, Seller


@shared_task
def daily_report_task():
    # Placeholder: implement your daily job logic here
    return "daily task executed"


@shared_task
def import_orders_from_excel(file_bytes: bytes, customer_id: int, seller_id: int, notify_email: str | None = None):
    df = pd.read_excel(BytesIO(file_bytes))
    # Expected columns: product_id, quantity, unit_price
    with transaction.atomic():
        customer = Customer.objects.get(pk=customer_id)
        seller = Seller.objects.get(pk=seller_id)
        order = Order.objects.create(customer=customer, seller=seller, amount=Decimal("0"))
        total = Decimal("0")
        items = []
        for _, row in df.iterrows():
            product = Product.objects.get(pk=int(row["product_id"]))
            quantity = int(row["quantity"]) 
            unit_price = Decimal(str(row.get("unit_price", product.amount)))
            subtotal = unit_price * quantity
            total += subtotal
            items.append(OrderItem(order=order, product=product, quantity=quantity, unit_price=unit_price, subtotal=subtotal))
        if items:
            OrderItem.objects.bulk_create(items)
        order.amount = total
        order.save(update_fields=["amount"])

    if notify_email:
        send_mail(
            subject="Orders Import Completed",
            message=f"Order {order.id} created with total amount {total}",
            from_email=None,
            recipient_list=[notify_email],
            fail_silently=True,
        )
    return {"order_id": order.id, "total": str(total)}


