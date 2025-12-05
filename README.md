# Elite Models Barcelona - Luxury Modeling Agency

A sophisticated luxury modeling agency platform featuring model portfolios, booking system, and admin management.

## 🌟 Features

### Client Features
- 🏛️ Elegant model directory with advanced filtering
- 📱 Responsive luxury design with white theme and pink accents
- 🔍 Search by city, age, height, and hair color
- 📋 Professional model profiles with photo galleries
- 📞 Direct booking system with contact forms
- 📝 Model application portal

### Admin Features
- 👑 Complete admin dashboard
- 👥 Model management (add, edit, approve)
- 📊 Booking management and client contact details
- 🏙️ City management
- 📸 Multi-photo upload system
- 🔐 Secure authentication

## 🚀 Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Session-based admin auth
- **File Upload**: Multi-photo management system

## 📦 Installation

1. **Clone the repository**
```bash
git clone https://github.com/lensordr/modelagency.git
cd modelagency
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd Restaurant
pip install -r requirements.txt
```

4. **Run the application**
```bash
python main.py
```

5. **Access the application**
- Public website: `http://localhost:8000/`
- Admin panel: `http://localhost:8000/admin/login`

## 🔑 Default Admin Login
- **Username**: admin
- **Password**: admin123

## 🏗️ Project Structure
```
modelagency/
├── Restaurant/
│   ├── main.py              # Main FastAPI application
│   ├── models.py            # Database models (Agency, Model, City, Booking, User)
│   ├── requirements.txt     # Python dependencies
│   ├── static/              # CSS, JS, images, uploads
│   └── templates/           # HTML templates
├── photos/                  # Sample images
├── .gitignore
└── README.md
```

## 🎨 Design Features
- **Luxury Aesthetic**: Clean white background with elegant pink accents
- **Responsive Design**: Mobile-first approach with Bootstrap 5
- **Professional Navigation**: Fixed header with smooth scrolling
- **Photo Galleries**: Carousel displays for model portfolios
- **Advanced Filtering**: Multi-criteria search functionality

## 🔐 Security Features
- Session-based authentication for admin panel
- Secure file upload handling
- Input validation and sanitization
- Protected admin routes

## 🌍 Deployment

### Heroku Deployment
The project includes Heroku configuration files:
- `Procfile`: Web server configuration
- `runtime.txt`: Python version specification
- `requirements.txt`: Dependencies

### Local Development
```bash
cd Restaurant
python main.py
```

## 📱 Mobile Responsive
- Touch-friendly interface
- Optimized for all screen sizes
- Fast loading with optimized images
- Smooth navigation experience

## 🎯 Key Models
- **Agency**: Main agency information
- **Model**: Model profiles with photos and details
- **City**: Location management
- **Booking**: Client booking requests
- **User**: Admin user management

## 🔄 Future Enhancements
- Payment integration
- Advanced analytics
- Multi-language support
- Email notifications
- API endpoints
- Mobile app

---
Built with ❤️ for luxury modeling agencies

## 📞 Contact
For inquiries about this platform, please visit the contact page or reach out through the booking system.