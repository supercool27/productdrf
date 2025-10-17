from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Prefetch

from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from .mixins import PlatformApiCallMixin
from .permissions import IsAdminOrReadOnly, IsSellerOrAdminOrReadOnly
from .decorators import customer_only_list


class ProductViewSet(PlatformApiCallMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


class OrderViewSet(PlatformApiCallMixin, viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsSellerOrAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["items__product__name"]  # icontains search via DRF
    ordering_fields = ["amount", "created_at", "id"]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = (
            Order.objects.select_related("customer", "seller")
            .prefetch_related("items__product")
            .all()
        )

        product_name = self.request.query_params.get("product")
        if product_name:
            qs = qs.filter(items__product__name__icontains=product_name)

        # Restrict by customer if decorator set _force_customer_id
        customer_id = getattr(self, "_force_customer_id", None)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)

        top = self.request.query_params.get("top")
        if top:
            try:
                top_n = int(top)
                qs = qs.order_by("-amount")[:top_n]
            except ValueError:
                pass

        return qs

    @action(detail=False, methods=["get"], url_path="top5")
    def top5(self, request):
        qs = self.get_queryset().order_by("-amount")[:5]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @customer_only_list
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["post"], url_path="import-excel")
    def import_excel(self, request):
        excel = request.FILES.get("file")
        customer_id = request.data.get("customer")
        seller_id = request.data.get("seller")
        notify_email = request.data.get("email")
        if not excel or not customer_id or not seller_id:
            return Response({"code": "bad_request", "message": "file, customer, seller required", "field_errors": None}, status=400)
        from .tasks import import_orders_from_excel

        import_orders_from_excel.delay(excel.read(), int(customer_id), int(seller_id), notify_email)
        return Response({"status": "queued"}, status=202)
