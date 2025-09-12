# TableLink - Restaurant Management System

A comprehensive restaurant management system with QR code ordering, real-time analytics, and business dashboard.

## Features

### Customer Features
- 📱 QR code table ordering
- 🍕 Interactive menu with customizations
- 💳 Tip selection and checkout
- 🔄 Real-time order status

### Business Features
- 📊 Live order dashboard
- 👨‍🍳 Waiter management
- 📈 Sales analytics (Business & Advanced)
- 📋 Menu management
- 💰 Financial reporting
- 📤 CSV/Excel export

### Analytics Dashboards
- **Business Dashboard**: Simple overview with period filtering (Today, Week, Month, Year)
- **Advanced Analytics**: Detailed analytics with waiter filtering, date selection, and comprehensive charts

## Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js
- **Authentication**: JWT tokens

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd TableLink
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd venv/Restaurant
pip install fastapi uvicorn sqlalchemy python-multipart python-jose[cryptography] passlib[bcrypt] pandas openpyxl
```

4. **Run the application**
```bash
python main.py
```

5. **Access the application**
- Customer ordering: `http://localhost:8000/table/{table_number}`
- Business dashboard: `http://localhost:8000/business/login`
- Advanced analytics: `http://localhost:8000/business/analytics`

## Default Login
- **Username**: admin
- **Password**: rrares

## Project Structure
```
TableLink/
├── venv/Restaurant/
│   ├── main.py              # Main FastAPI application
│   ├── models.py            # Database models
│   ├── crud.py              # Database operations
│   ├── analytics_service.py # Analytics functions
│   ├── auth.py              # Authentication
│   ├── setup.py             # Initial setup
│   ├── static/              # CSS, JS, images
│   └── templates/           # HTML templates
├── .gitignore
└── README.md
```

## Key Features Implemented

### 🎯 Order Management
- Real-time order tracking
- Table status management
- Waiter assignment
- Tip handling

### 📊 Analytics System
- Dual dashboard system (Business + Advanced)
- Period-based filtering (Day, Week, Month, Year)
- Waiter performance tracking
- Category analysis
- Sales trends
- Export functionality

### 🔐 Security
- JWT authentication
- Role-based access
- Secure password hashing

### 📱 Mobile-Friendly
- Responsive design
- QR code integration
- Touch-friendly interface

## Development Notes
- Uses test data from September 2025 for analytics demonstration
- Real-time analytics updates when new orders are processed
- Supports both individual item tracking and order-level analytics
- Comprehensive waiter filtering across all analytics views

## Future Enhancements
- Payment integration
- Inventory management
- Multi-restaurant support
- Advanced reporting
- Mobile app

---
Built with ❤️ for restaurant efficiency