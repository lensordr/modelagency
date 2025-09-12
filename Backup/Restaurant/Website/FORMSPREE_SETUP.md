# Formspree Setup Instructions

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Formspree Account
1. Go to https://formspree.io
2. Sign up with your email: **lens.ordr@gmail.com**
3. Verify your email

### Step 2: Create Forms
1. Click "New Form" 
2. Create **2 forms**:
   - **Trial Form**: Name it "TablePulse Trial Requests"
   - **Contact Form**: Name it "TablePulse Contact"

### Step 3: Get Form IDs
After creating each form, you'll get URLs like:
- `https://formspree.io/f/abc123def` 

Copy the **abc123def** part (your form ID)

### Step 4: Update Website
Replace in `index.html`:
- `YOUR_FORM_ID` → your trial form ID
- `YOUR_CONTACT_FORM_ID` → your contact form ID

**Example:**
```html
<!-- Change this -->
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">

<!-- To this -->
<form action="https://formspree.io/f/abc123def" method="POST">
```

### Step 5: Test
1. Open your website
2. Fill out the trial form
3. Submit
4. Check your email: **lens.ordr@gmail.com**

## ✅ What You'll Receive

### Trial Form Submissions:
```
Subject: New TablePulse Trial Request
From: noreply@formspree.io

Restaurant Name: [Name]
Email: [Email]
Phone: [Phone]
Restaurant Type: [Type]
```

### Contact Form Submissions:
```
Subject: TablePulse Contact Form
From: noreply@formspree.io

Name: [Name]
Email: [Email]
Message: [Message]
```

## 🆓 Free Plan Limits
- **50 submissions/month** (perfect for starting)
- Upgrade later if needed

## 🔧 Advanced Options (Optional)
- **Custom Thank You Page**: Set redirect after submission
- **Spam Protection**: Enable reCAPTCHA
- **Webhooks**: Connect to other services
- **Email Templates**: Customize notification emails

## 📧 Next Steps After Setup
1. **Respond Quickly**: Reply to trial requests within 24 hours
2. **Create Process**: Have a system to set up actual trials
3. **Track Leads**: Keep spreadsheet of requests
4. **Follow Up**: Send demo links or schedule calls