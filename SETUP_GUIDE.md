# Bullstrap Price Tracker Setup Guide

## Overview
This automated price tracker monitors the Bullstrap Contemporary Case (TERRA) daily and sends you an email alert whenever the price changes.

**Current Price:** $71 (was $89) — 20% off  
**Email Recipient:** nrkws@outlook.com

---

## Prerequisites
- GitHub account (free)
- Gmail account with 2FA enabled (for sending alerts)

---

## Setup Steps

### 1. Create a GitHub Repository
1. Go to [github.com](https://github.com) and log in
2. Create a **new public repository** named `bullstrap-tracker`
3. Add a description: "Daily price tracking for Bullstrap Contemporary Case"
4. Initialize with README

### 2. Add Files to Your Repository
Upload these files to your repo:

**File 1: `bullstrap_tracker.py`** (provided below)  
**File 2: `.github/workflows/price_tracker.yml`** (provided below)  
**File 3: `bullstrap_price_history.json`** (create empty file):
```json
{}
```

You can upload via:
- **GitHub Web UI:** Click "Add file" → "Upload files"
- **Git CLI:** Clone repo, add files, `git push`

### 3. Set Up Gmail App Password (for email alerts)

Since Gmail requires app-specific passwords for automated access:

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (if not already enabled)
3. Go back to Security → "App passwords"
4. Select: **Mail** + **Windows Computer** (or your device)
5. Google generates a **16-character password** → **Copy it**

### 4. Add GitHub Secrets
1. Go to your GitHub repo
2. Settings → Secrets and variables → Actions
3. Create two secrets:

| Secret Name | Value |
|---|---|
| `EMAIL_USER` | your-email@gmail.com |
| `EMAIL_PASSWORD` | 16-char-app-password (from step 3) |

⚠️ **Important:** Use the 16-character app password, NOT your regular Gmail password

### 5. Enable GitHub Actions
1. Go to repo → Actions tab
2. Click "I understand my workflows, go ahead and enable them"

### 6. Test the Workflow
1. Go to Actions tab
2. Click "Bullstrap Price Tracker" workflow
3. Click "Run workflow" → "Run workflow"
4. Wait ~1 minute for execution
5. Check your email (nrkws@outlook.com) for test alert

### 7. Automatic Daily Checks
The tracker now runs **automatically every day at 9:00 AM UTC** (4:00 AM CT / 5:00 AM ET).

- To change the time, edit `.github/workflows/price_tracker.yml` line 6
- Cron format: `'0 9 * * *'` means 9:00 AM UTC daily
- [Convert your timezone](https://www.unixtimestamp.com/timezones.php)

---

## How It Works

1. **Daily Check:** Script fetches current price from Bullstrap
2. **Compare:** Checks against saved price in `bullstrap_price_history.json`
3. **Alert:** If price changed, sends HTML email showing:
   - Previous price
   - Current price
   - Dollar & percentage change
   - Stock status
4. **Log:** Updates history file (stored in repo)

---

## Email Alert Format

When price changes, you'll receive an email like:

```
🔔 Price Alert: The New Contemporary Case - TERRA

Product: The New Contemporary Case - TERRA
URL: https://bullstrap.co/products/the-new-contemporary-case-terra

Previous Price: $89.00
Current Price: $71.00
Change: -$18.00 (-20.2%)

Stock Status: ✅ In Stock
```

---

## Troubleshooting

### Emails not arriving
- Check GitHub Actions logs (Actions tab → workflow run → job logs)
- Verify email secrets are set correctly
- Check spam/junk folder
- Ensure Gmail 2FA and app password are configured

### Workflow not running
- Enable Actions in Settings
- Check cron schedule matches your timezone
- Manually trigger via "Run workflow" button

### Script errors
- Check Actions logs for error messages
- Ensure `bullstrap_price_history.json` exists
- Verify Python 3.11 compatibility

---

## Customization

### Change check frequency
Edit `.github/workflows/price_tracker.yml` line 6:
```yaml
- cron: '0 9 * * *'  # Daily at 9 AM
- cron: '0 */6 * * *'  # Every 6 hours
- cron: '0 9 * * 1'  # Weekly (Mondays at 9 AM)
```

### Change recipient email
Edit `bullstrap_tracker.py` line 17:
```python
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "your-email@example.com")
```

### Track different Bullstrap product
1. Update `PRODUCT_URL` and `VARIANT_ID` in script
2. Rename repository/workflow accordingly

---

## Cost
✅ **Completely Free**
- GitHub Actions: Free tier (2000 minutes/month)
- Gmail: Free
- Total: $0

---

## Questions?
If tracking stops or errors occur, check the GitHub Actions tab for logs. Most issues are credential-related.

Good luck! 🚀
