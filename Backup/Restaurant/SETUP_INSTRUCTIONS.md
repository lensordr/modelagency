# TablePulse Setup Instructions

## 🚀 First Time Setup

When you start TablePulse for the first time, you'll see the **Setup Wizard**:

### Step 1: Restaurant Configuration
```
Enter your restaurant name: My Amazing Restaurant
```

### Step 2: Admin Account Setup  
```
Enter admin username: admin
Enter admin password: your_secure_password
```

### Step 3: Menu Setup
```
Do you want to upload a menu file now?
1. Yes - I have an Excel/PDF file
2. No - I'll add items manually later

Choose (1 or 2): 1
Enter full path to your menu file: C:\path\to\your\menu.xlsx
```

## 📁 Menu File Formats

### Excel Format (.xlsx, .xls)
| Column A | Column B | Column C | Column D |
|----------|----------|----------|----------|
| Name | Ingredients | Price | Category |
| Pizza Margherita | Tomato, Mozzarella, Basil | 12.50 | Food |
| Coca Cola | Carbonated Water, Sugar | 2.50 | Drinks |

### PDF Format
```
Pizza Margherita - 12.50 - Tomato, Mozzarella, Basil - Food
Coca Cola - 2.50 - Carbonated Water, Sugar - Drinks
```

## ✅ After Setup

1. **Access Business Dashboard**: http://localhost:8001/business
2. **Login** with your admin credentials
3. **Client Access**: http://localhost:8001/client?table=1
4. **Restaurant name** appears on client interface

## 🔄 Re-running Setup

To reset and run setup again:
1. Delete `setup_complete.json` file
2. Restart the server
3. Setup wizard will run again

## 📋 What Gets Created

- ✅ Admin user account
- ✅ Restaurant configuration
- ✅ Menu items (if file provided)
- ✅ Sample tables (1-10)
- ✅ Default table codes

## 🛠️ Manual Configuration

If you skip menu upload, you can:
- Upload menu files from Business Dashboard
- Add menu items manually
- Configure settings later