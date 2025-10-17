from django.core.management.base import BaseCommand
from products.models import Product


SAMPLE_PRODUCTS = [
    ("RONEMOX 250MG - GY CAPSULE 10S", 9375),
    ("RONEMOX 250MG CAPSULES 10’S", 9375),
    ("SAFEROXIM 500 TABLET", 19638),
    ("AMOXYCLAV DRY SYRUP 30ML HDPE BOTTLE", 10400),
    ("ABBOTT GRIPE WATER", 4200),
    ("ZITHROLECT 250 TABS 6S", 41040),
    ("AMOXYCLAV 375 MG TABLETS", 18560),
    ("SCABIGARD 100ML", 2650),
    ("SAFEXIM 100 TABLET", 2450),
    ("ZITHROLECT 500 TABS 3S", 6840),
    ("SAFEXIM 200 TABLET", 19980),
    ("PHENSEDYL DX 60 ML SYRUP", 16250),
    ("SCABIGARD-P LOTION 50ML", 3800),
    ("SAFEROXIM 500 TABLET", 46913),
    ("NCAL TABLETS 15S", 9520),
    ("AB-ROZU 5 TABLETS", 720),
    ("NKACIN 500MG INJ", 24600),
    ("ZITHROLECT 500 TABS 3S", 34200),
    ("SUPERQUIN 500MG TABLETS 5S", 1750),
    ("AMOXYCLAV 1GM TABLET", 3270),
]


class Command(BaseCommand):
    help = "Seed sample products"

    def handle(self, *args, **options):
        created = 0
        for name, amount in SAMPLE_PRODUCTS:
            # Normalize duplicate names by case
            existing = Product.all_objects.filter(name__iexact=name).first()
            if existing:
                if existing.is_deleted or existing.amount != amount:
                    existing.is_deleted = False
                    existing.amount = amount
                    existing.save(update_fields=["is_deleted", "amount"])
                continue
            Product.objects.create(name=name, amount=amount)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} products"))


