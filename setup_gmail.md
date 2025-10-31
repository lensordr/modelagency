# Gmail Setup for Hotel Email Campaign

## Step 1: Enable Gmail App Password

1. **Go to Google Account Settings**
   - Visit [myaccount.google.com](https://myaccount.google.com)
   - Click "Security" in left menu

2. **Enable 2-Step Verification** (if not already enabled)
   - Click "2-Step Verification"
   - Follow setup process

3. **Generate App Password**
   - Go back to Security
   - Click "App passwords"
   - Select "Mail" and "Other (Custom name)"
   - Name it "TableLink Campaign"
   - Copy the 16-character password

## Step 2: Set Environment Variables

```bash
export SENDER_EMAIL="your-gmail@gmail.com"
export SENDER_APP_PASSWORD="abcd efgh ijkl mnop"  # 16-char password from step 1
```

## Step 3: Run Email Campaign

```bash
# First, scrape hotels
python scrape_hotels_places_only.py

# Then send emails
python email_sender.py
```

## Email Features

✅ **Professional HTML template**
✅ **Personalized for each hotel**
✅ **TableLink branding and benefits**
✅ **Call-to-action buttons**
✅ **Spam-compliant delays**
✅ **Success/failure tracking**

## Campaign Results

- Reads from `barcelona_hotels_emails.csv`
- Removes duplicate emails
- 30-second delay between emails
- Professional TableLink pitch
- Tracks sent/failed counts

## Legal Compliance

- Includes unsubscribe option
- Business-to-business communication
- Legitimate business interest
- Professional sender identification