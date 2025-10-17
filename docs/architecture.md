# Architecture Overview

- App: `products`
- API: DRF ViewSets, versioned under `/api/v1/...`
- Auth: SimpleJWT
- Permissions: Admin, Seller, Customer roles
- Data Model:
  - `Customer`, `Seller` -> link to `User`
  - `Product`
  - `Order` with `OrderItem` (quantity, unit_price, subtotal)
  - `PlatformApiCall` audit log
- Persistence:
  - Soft-deletes and timestamps via `TimeStampedSoftDeleteModel`
- Logging:
  - `AuditLoggingMiddleware` (request/response meta)
  - `PlatformApiCallMixin` (per-view payload logging)
- Async:
  - Celery app in `products.celery_app`
  - Beat schedule at 14:30 Asia/Kolkata
  - Tasks: `daily_report_task`, `import_orders_from_excel`
- Performance:
  - `select_related` on FKs, `prefetch_related` on reverse relations
  - Bulk operations for imports
- Docs:
  - drf-spectacular for schema and Swagger UI

Sequence (Order Create):
1. Client POSTs `/api/v1/orders/` with items
2. Serializer validates, creates `Order`, bulk creates `OrderItem`s, computes amount
3. Viewset returns order with derived `products` and `items_read`
4. Mixins/middleware log request/response

Sequence (Excel Import):
1. Client POSTs `/api/v1/orders/import-excel`
2. View enqueues `import_orders_from_excel`
3. Task parses Excel, creates `Order` + bulk `OrderItem`s, updates amount
4. Optional email summary is sent
