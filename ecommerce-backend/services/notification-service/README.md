# Notification Service

## Purpose
Sends email notifications based on events from other services.

## Responsibilities
- Send welcome emails
- Order confirmation emails
- Payment receipts
- Order status update emails
- Password reset emails

## Email Service
- AWS SES or Django SMTP

## Async Processing
- Celery for background task processing

## Notification Templates
- Welcome email
- Order confirmation
- Payment receipt
- Order shipped
- Order delivered
- Password reset

## APIs (To be implemented)
- POST `/api/notifications/send` - Send notification (Internal use)
- GET `/api/notifications/history/:userId` - Get notification history

## Kafka Events (Consumer)
Listens to events from other services:
- `user.registered` → Send welcome email
- `order.created` → Send order confirmation
- `payment.confirmed` → Send payment receipt
- `order.shipped` → Send shipping notification
- `order.delivered` → Send delivery confirmation
- `user.password.reset.requested` → Send reset link
