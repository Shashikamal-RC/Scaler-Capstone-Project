# Order Service

## Purpose
Handles order processing, tracking, and history.

## Responsibilities
- Create orders from cart
- Order status management
- Order history
- Order tracking
- Integration with Payment Service

## Database
- PostgreSQL
- Tables: Orders, OrderItems, OrderStatusHistory

## APIs (To be implemented)
- POST `/api/orders` - Create new order
- GET `/api/orders` - Get user's order history
- GET `/api/orders/:id` - Get order details
- PUT `/api/orders/:id/status` - Update order status (Admin)
- GET `/api/orders/:id/tracking` - Track order delivery

## Order Status Flow
1. PENDING - Order created, awaiting payment
2. CONFIRMED - Payment confirmed
3. PROCESSING - Being prepared
4. SHIPPED - Out for delivery
5. DELIVERED - Completed
6. CANCELLED - Cancelled by user/admin

## Kafka Events
**Producer:**
- `order.created` - When order is placed
- `order.confirmed` - When payment confirmed
- `order.shipped` - When order shipped
- `order.delivered` - When order delivered
- `order.cancelled` - When order cancelled

**Consumer:**
- `payment.confirmed` - Update order status
- `payment.failed` - Cancel order
