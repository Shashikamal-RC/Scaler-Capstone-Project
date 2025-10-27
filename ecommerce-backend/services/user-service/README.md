# User Service

## Purpose
Handles all user-related operations including authentication and authorization.

## Responsibilities
- User registration
- User login with JWT authentication
- Profile management (view/update)
- Password reset
- Role-based access control (RBAC)

## Database
- PostgreSQL
- Tables: Users, Roles, Permissions

## APIs (To be implemented)
- POST `/api/users/register` - Register new user
- POST `/api/users/login` - User login
- GET `/api/users/profile` - Get user profile
- PUT `/api/users/profile` - Update user profile
- POST `/api/users/reset-password` - Reset password

## Kafka Events (Producer)
- `user.registered` - When new user registers
- `user.profile.updated` - When user updates profile
