# Cart Service

## Purpose
Manages user shopping carts with fast access and caching.

## Responsibilities
- Add/remove/update cart items
- View cart with totals
- Cart expiration logic
- Calculate cart totals (with tax and discounts)

## Database
- MongoDB (flexible schema for cart items)

## Cache
- Redis for fast cart data access

## APIs (To be implemented)
- GET `/api/cart` - Get user's cart
- POST `/api/cart/items` - Add item to cart
- PUT `/api/cart/items/:id` - Update cart item quantity
- DELETE `/api/cart/items/:id` - Remove item from cart
- DELETE `/api/cart` - Clear entire cart
- GET `/api/cart/total` - Get cart total

## Kafka Events (Producer)
- `cart.item.added` - When item added to cart
- `cart.item.removed` - When item removed from cart
- `cart.cleared` - When cart is cleared after checkout
