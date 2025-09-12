# 🔐 Restaurant Authentication System

## Overview
We've successfully implemented **JWT-based authentication** with role-based access control for your Restaurant Management System.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4
```

### 2. Start the Server
```bash
python start_server.py
```

### 3. Access the System
- **Business Login**: http://localhost:8001/business/login
- **Business Dashboard**: http://localhost:8001/business (requires login)
- **Client Interface**: http://localhost:8001/client?table=1 (no auth required)

## 🔑 Default Credentials
- **Username**: `admin`
- **Password**: `rrares`
- **Role**: `admin` (full access)

## 🏗️ Architecture

### Authentication Flow
1. **Login** → User submits credentials
2. **Validation** → Server verifies username/password
3. **JWT Token** → Server returns signed JWT token
4. **Authorization** → Client includes token in requests
5. **Verification** → Server validates token for protected routes

### Security Features
- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: 8-hour expiration
- **Role-based Access**: Admin vs Waiter permissions
- **Automatic Logout**: On token expiration
- **Protected Routes**: All business endpoints secured

## 📁 New Files Added

### `auth.py`
- JWT token creation/verification
- Password hashing utilities
- User authentication functions
- Role-based access decorators

### `templates/login.html`
- Clean login interface
- JavaScript for token handling
- Error message display
- Automatic redirect after login

### Database Changes
- **New Table**: `users` (id, username, password_hash, role, active, created_at)
- **Default Admin**: Created automatically on startup

## 🛡️ Protected Routes

### Admin Only (`require_admin`)
- `POST /business/upload_menu` - Menu file upload
- `POST /business/toggle_product/{id}` - Enable/disable menu items
- `GET /business/waiters` - View waiters
- `POST /business/waiters` - Add waiter
- `DELETE /business/waiters/{id}` - Remove waiter

### Authenticated Users (`get_current_user`)
- `GET /business/dashboard` - Table overview
- `GET /business/order_details/{table}` - Order details
- `POST /business/finish_table/{table}` - Complete orders
- `GET /business/sales` - Sales analytics
- `GET /business/menu_items` - Menu management

### Public Routes (No Auth)
- `GET /client` - Customer interface
- `GET /client/menu` - Menu display
- `POST /client/order` - Place orders
- `POST /client/checkout` - Request checkout

## 🔧 Frontend Changes

### Business Dashboard
- **Authentication Check**: Redirects to login if no token
- **Auto-logout**: On 401 responses
- **Token Headers**: All API calls include Bearer token
- **Logout Button**: Clear token and redirect

### Login Page
- **Form Validation**: Client-side validation
- **Token Storage**: localStorage for persistence
- **Error Handling**: User-friendly error messages
- **Auto-redirect**: To dashboard after successful login

## 🧪 Testing

### Manual Testing
1. Visit `/business` → Should redirect to login
2. Login with wrong credentials → Should show error
3. Login with correct credentials → Should access dashboard
4. Try accessing protected routes → Should work with token
5. Clear localStorage → Should redirect to login

### Automated Testing
```bash
# Install requests if needed
pip install requests

# Run authentication tests
python test_auth.py
```

## 🔄 User Management

### Adding New Users (Admin Only)
Currently, users must be added programmatically. You can extend the system by:

1. **Adding User Management UI** in the business dashboard
2. **Creating API endpoints** for user CRUD operations
3. **Implementing user roles** (admin, manager, waiter)

### Example: Add User Programmatically
```python
from crud import create_user
from models import get_db

db = next(get_db())
create_user(db, "waiter1", "password123", "waiter")
```

## 🚨 Security Considerations

### Production Deployment
1. **Change Secret Key**: Update `SECRET_KEY` in `auth.py`
2. **Use Environment Variables**: Store secrets in env vars
3. **HTTPS Only**: Enable SSL/TLS in production
4. **Token Expiration**: Consider shorter expiration times
5. **Rate Limiting**: Add login attempt limits

### Current Security Features
- ✅ Password hashing with bcrypt
- ✅ JWT token expiration
- ✅ Role-based access control
- ✅ Automatic token validation
- ✅ Secure logout functionality

## 🎯 Next Steps

### Recommended Enhancements
1. **User Management Interface** - Add/edit/delete users via UI
2. **Password Reset** - Email-based password recovery
3. **Session Management** - Track active sessions
4. **Audit Logging** - Log authentication events
5. **Two-Factor Authentication** - Enhanced security
6. **Remember Me** - Longer-lived tokens option

### Integration Ideas
1. **Waiter Accounts** - Individual waiter logins
2. **Shift Management** - Track waiter work hours
3. **Permission Granularity** - Fine-grained access control
4. **Multi-restaurant** - Support multiple locations

## 📞 Support

The authentication system is now fully integrated and ready for use. The client interface remains unchanged and doesn't require authentication, while all business operations are now properly secured.

**Default Access:**
- Username: `admin`
- Password: `rrares`
- Full administrative access to all features

Enjoy your secure restaurant management system! 🍽️✨