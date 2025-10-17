from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Customer, Seller


class Command(BaseCommand):
    help = "Create sample Customer and Seller users and profiles"

    def handle(self, *args, **options):
        User = get_user_model()

        cust_user, _ = User.objects.get_or_create(
            username="customer1",
            defaults={"email": "customer1@example.com"},
        )
        if not cust_user.has_usable_password():
            cust_user.set_password("Customer@123")
            cust_user.save()
        customer, _ = Customer.all_objects.get_or_create(
            user=cust_user,
            defaults={"name": "Customer One", "mobile": "9999999999"},
        )

        sell_user, _ = User.objects.get_or_create(
            username="seller1",
            defaults={"email": "seller1@example.com"},
        )
        if not sell_user.has_usable_password():
            sell_user.set_password("Seller@123")
            sell_user.save()
        seller, _ = Seller.all_objects.get_or_create(
            user=sell_user,
            defaults={"name": "Seller One", "mobile": "8888888888"},
        )

        self.stdout.write(self.style.SUCCESS("Seeded sample customer and seller users."))

