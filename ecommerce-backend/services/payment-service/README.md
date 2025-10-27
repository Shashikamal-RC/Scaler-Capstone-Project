# Payment Service

## Purpose
Manages payment processing and transaction logs.

## Responsibilities
- Payment gateway integration (Stripe/Razorpay mock)
- Process payments
- Transaction logging
- Payment status updates
- Refund handling

## Database
- PostgreSQL
- Tables: Transactions, PaymentMethods

## APIs (To be implemented)
- POST `/api/payments` - Process payment
- GET `/api/payments/:id` - Get payment details
- POST `/api/payments/:id/refund` - Process refund (Admin)
- GET `/api/payments/transaction/:id` - Get transaction details

## Payment Status
- PENDING - Payment initiated
- PROCESSING - Payment being processed
- SUCCESS - Payment successful
- FAILED - Payment failed
- REFUNDED - Payment refunded

## Kafka Events
**Producer:**
- `payment.initiated` - When payment starts
- `payment.confirmed` - When payment succeeds
- `payment.failed` - When payment fails
- `payment.refunded` - When payment refunded

**Consumer:**
- `order.created` - Process payment for order
