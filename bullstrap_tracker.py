#!/usr/bin/env python3
"""
Bullstrap Price Tracker
Tracks daily price changes for Bullstrap Contemporary Case Terra
Sends email alert when price changes
"""

import requests
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
PRODUCT_ID = "46006040723650"
PRODUCT_URL = "https://bullstrap.co/products/the-contemporary-plateau-sienna"     
PRODUCT_NAME = "The Contemporary Plateau Sienna"
VARIANT_ID = "46006040723650"

# Email Configuration - uses environment variables (set in GitHub Secrets)
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "nrkws@outlook.com")

# Price tracking file (stored in repo)
PRICE_FILE = "bullstrap_price_history.json"


def fetch_price():
    """
    Fetch current price from Bullstrap using Shopify GraphQL API
    Returns: (price, currency, status)
    """
    try:
        # Bullstrap uses Shopify - fetch product info
        api_url = "https://bullstrap.co/products/the-contemporary-plateau-sienna.json"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        product = data.get("product", {})
        
        # Find the variant
        variants = product.get("variants", [])
        target_variant = None
        
        for variant in variants:
            # Match by variant ID or find TERRA variant
            if str(variant.get("id")) == VARIANT_ID or "SIENNA" in str(variant.get("title", "")):
                target_variant = variant
                break
        
        if not target_variant:
            target_variant = variants[0] if variants else None
        
        if target_variant:
            price = target_variant.get("price")
            currency = product.get("vendor", "USD")  # Fallback
            available = target_variant.get("available", False)
            
            return {
                "price": float(price) if price else None,
                "compare_price": float(target_variant.get("compare_at_price") or price),
                "available": available,
                "timestamp": datetime.now().isoformat(),
                "title": target_variant.get("title", PRODUCT_NAME)
            }
        
        return None
        
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def load_price_history():
    """Load previous price data"""
    if os.path.exists(PRICE_FILE):
        try:
            with open(PRICE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_price_history(history):
    """Save price history"""
    with open(PRICE_FILE, "w") as f:
        json.dump(history, f, indent=2)


def send_email(subject, body, html_body=None):
    """Send email notification"""
    try:
        # Check if credentials exist
        if not EMAIL_USER or not EMAIL_PASSWORD:
            print("Email credentials not configured. Skipping email.")
            return False
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_RECIPIENT
        
        # Attach plain text
        msg.attach(MIMEText(body, "plain"))
        
        # Attach HTML if provided
        if html_body:
            msg.attach(MIMEText(html_body, "html"))
        
        # Send via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, EMAIL_RECIPIENT, msg.as_string())
        
        print(f"Email sent to {EMAIL_RECIPIENT}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def format_email(previous_price, current_price, available, title):
    """Format email notification"""
    
    # Calculate change
    if previous_price and current_price:
        change = current_price - previous_price
        percent_change = (change / previous_price) * 100
        change_str = f"${change:+.2f} ({percent_change:+.1f}%)"
    else:
        change_str = "N/A"
    
    status = "✅ In Stock" if available else "❌ Out of Stock"
    
    subject = f"🔔 Price Alert: {title}"
    
    body = f"""
Bullstrap Price Tracker Alert

Product: {title}
URL: {PRODUCT_URL}

Previous Price: ${previous_price:.2f}
Current Price: ${current_price:.2f}
Change: {change_str}

Stock Status: {status}

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
This is an automated price tracking alert.
"""
    
    html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2>🔔 Price Alert: {title}</h2>
    <p><strong>Product:</strong> {title}</p>
    <p><strong>URL:</strong> <a href="{PRODUCT_URL}">{PRODUCT_URL}</a></p>
    
    <table border="1" cellpadding="10" style="border-collapse: collapse;">
      <tr>
        <td><strong>Previous Price</strong></td>
        <td style="color: #666;">${previous_price:.2f}</td>
      </tr>
      <tr>
        <td><strong>Current Price</strong></td>
        <td style="color: #d63031; font-weight: bold;">${current_price:.2f}</td>
      </tr>
      <tr>
        <td><strong>Change</strong></td>
        <td style="color: {'#27ae60' if change < 0 else '#e74c3c'}; font-weight: bold;">{change_str}</td>
      </tr>
    </table>
    
    <p><strong>Stock Status:</strong> {status}</p>
    <p style="color: #666; font-size: 12px;">Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
  </body>
</html>
"""
    
    return subject, body, html_body


def main():
    """Main tracking function"""
    print(f"[{datetime.now()}] Starting Bullstrap price check...")
    
    # Fetch current price
    current_data = fetch_price()
    
    if not current_data:
        print("Failed to fetch price data")
        return
    
    current_price = current_data["price"]
    print(f"Current price: ${current_price:.2f} (Available: {current_data['available']})")
    
    # Load history
    history = load_price_history()
    last_data = history.get("last_check", {})
    last_price = last_data.get("price")
    
    # Check if price changed
    price_changed = last_price and current_price != last_price
    
    if price_changed:
        print(f"⚠️ Price changed! Was: ${last_price:.2f}, Now: ${current_price:.2f}")
        
        subject, body, html_body = format_email(
            last_price,
            current_price,
            current_data["available"],
            current_data["title"]
        )
        
        send_email(subject, body, html_body)
    else:
        if last_price:
            print(f"✓ Price unchanged: ${current_price:.2f}")
        else:
            print(f"✓ First check recorded: ${current_price:.2f}")
    
    # Save current data
    history["last_check"] = current_data
    history["checks"] = history.get("checks", [])
    history["checks"].append(current_data)
    
    # Keep only last 90 days of history
    history["checks"] = history["checks"][-90:]
    
    save_price_history(history)
    print("History saved.")


if __name__ == "__main__":
    main()
