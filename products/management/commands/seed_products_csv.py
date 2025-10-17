import csv
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from products.models import Product


class Command(BaseCommand):
    help = "Seed products from a CSV file with columns: product_name, amount"

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True, help="Path to CSV file")

    def handle(self, *args, **options):
        path = Path(options["path"]).resolve()
        if not path.exists():
            raise CommandError(f"CSV not found: {path}")

        created, updated, revived = 0, 0, 0
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("product_name") or row.get("name") or "").strip()
                amount_raw = (row.get("amount") or row.get("price") or "0").strip()
                if not name:
                    continue
                try:
                    amount = Decimal(str(amount_raw))
                except Exception:
                    self.stdout.write(self.style.WARNING(f"Skip '{name}': invalid amount '{amount_raw}'"))
                    continue

                existing = Product.all_objects.filter(name__iexact=name).first()
                if existing:
                    changed = False
                    if existing.is_deleted:
                        existing.is_deleted = False
                        revived += 1
                        changed = True
                    if existing.amount != amount:
                        existing.amount = amount
                        updated += 1
                        changed = True
                    if changed:
                        existing.save(update_fields=["is_deleted", "amount"])
                else:
                    Product.objects.create(name=name, amount=amount)
                    created += 1

        self.stdout.write(self.style.SUCCESS(f"Products created={created}, updated={updated}, revived={revived}"))


