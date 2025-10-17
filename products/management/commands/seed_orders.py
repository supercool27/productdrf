from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from products.models import Customer, Seller, Product, Order, OrderItem


class Command(BaseCommand):
    help = "Create sample orders with items for testing filters and sorting"

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        customer_user = User.objects.get(username="customer1")
        seller_user = User.objects.get(username="seller1")
        customer = Customer.objects.get(user=customer_user)
        seller = Seller.objects.get(user=seller_user)

        products = list(Product.objects.all()[:5])
        if len(products) < 3:
            self.stdout.write(self.style.WARNING("Not enough products to seed orders."))
            return

        # Order 1 - higher amount, contains product[0]
        order1 = Order.objects.create(customer=customer, seller=seller, amount=Decimal("0"))
        total1 = Decimal("0")
        items1 = [
            (products[0], 3),
            (products[1], 2),
        ]
        for product, qty in items1:
            unit = Decimal(product.amount)
            subtotal = unit * qty
            OrderItem.objects.create(order=order1, product=product, quantity=qty, unit_price=unit, subtotal=subtotal)
            total1 += subtotal
        order1.amount = total1
        order1.save(update_fields=["amount"])

        # Order 2 - lower amount, contains product[2]
        order2 = Order.objects.create(customer=customer, seller=seller, amount=Decimal("0"))
        total2 = Decimal("0")
        items2 = [
            (products[2], 1),
        ]
        for product, qty in items2:
            unit = Decimal(product.amount)
            subtotal = unit * qty
            OrderItem.objects.create(order=order2, product=product, quantity=qty, unit_price=unit, subtotal=subtotal)
            total2 += subtotal
        order2.amount = total2
        order2.save(update_fields=["amount"])

        self.stdout.write(self.style.SUCCESS(f"Created orders: {order1.id}, {order2.id}"))


