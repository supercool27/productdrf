from typing import Any

from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from .models import Product, Order, OrderItem, Customer, Seller


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "amount"]

    def validate_name(self, value: str) -> str:
        qs = Product.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Product with this name already exists.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.ListSerializer(child=serializers.DictField(), write_only=True)
    products = serializers.SerializerMethodField(read_only=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    seller = serializers.PrimaryKeyRelatedField(queryset=Seller.objects.all())
    items_read = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "seller",
            "products",
            "items",
            "items_read",
            "amount",
            "created_at",
        ]
        read_only_fields = ["created_at", "items_read"]

    def get_items_read(self, obj: Order):
        return [
            {
                "product": item.product_id,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
                "subtotal": str(item.subtotal),
            }
            for item in obj.items.select_related("product").all()
        ]

    def get_products(self, obj: Order):
        return [item.product_id for item in obj.items.all()]

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> Order:
        items_payload = validated_data.pop("items", [])
        order = Order.objects.create(**validated_data)
        total = Decimal("0")
        created_items: list[OrderItem] = []
        for row in items_payload:
            product = Product.objects.get(pk=row["product"])  # will raise 404 upstream on validation if needed
            quantity = int(row.get("quantity", 1))
            unit_price = Decimal(str(row.get("unit_price", product.amount)))
            subtotal = unit_price * quantity
            total += subtotal
            created_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal,
                )
            )
        if created_items:
            OrderItem.objects.bulk_create(created_items)
        order.amount = total
        order.save(update_fields=["amount"])
        return order

    @transaction.atomic
    def update(self, instance: Order, validated_data: dict[str, Any]) -> Order:
        items_payload = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_payload is not None:
            instance.items.all().delete()
            total = Decimal("0")
            created_items: list[OrderItem] = []
            for row in items_payload:
                product = Product.objects.get(pk=row["product"]) 
                quantity = int(row.get("quantity", 1))
                unit_price = Decimal(str(row.get("unit_price", product.amount)))
                subtotal = unit_price * quantity
                total += subtotal
                created_items.append(
                    OrderItem(
                        order=instance,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        subtotal=subtotal,
                    )
                )
            if created_items:
                OrderItem.objects.bulk_create(created_items)
            instance.amount = total
            instance.save(update_fields=["amount"])
        return instance


