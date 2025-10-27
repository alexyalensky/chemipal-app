# Git Credentials Setup

## ⚠️ Security Alert

**Never share your GitHub password in chat!** This has been logged and you should change your password immediately.

---

## Recommended: Use Personal Access Token

GitHub no longer accepts passwords for Git operations. Here's how to set up proper authentication:

### Step 1: Create Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Name: `chemipal-app-token`
4. Expiration: Set to your preference (e.g., 90 days)
5. Select scopes:
   - ✅ **repo** (Full control of private repositories)
6. Click **"Generate token"**
7. **Copy the token immediately** - it starts with `ghp_...`
8. You won't see it again!

### Step 2: Use Token for Authentication

When prompted for password during `git push`, paste the token instead of your password.

Or configure Git to store it:

```powershell
git config --global credential.helper wincred
```

Then when you push, enter:
- Username: `alexyalensky`
- Password: (paste your token)

---

## Quick Setup Right Now

Run these commands:

```powershell
# Set up credential helper (one time)
git config --global credential.helper wincred

# Push to GitHub (will prompt for credentials)
git push origin main
```

When prompted:
- **Username**: alexyalensky
- **Password**: (paste your Personal Access Token, NOT your actual password)

---

## Alternative: GitHub CLI

Install GitHub CLI for easier authentication:

```powershell
# Install via winget or chocolatey
winget install GitHub.cli

# Authenticate
gh auth login

# Push
git push origin main
```

---

## Current Status

Your repository is already set up and connected to GitHub. You just need to authenticate to push.

**Your repository URL**: https://github.com/alexyalensky/chemipal-app

### To push your code:

```powershell
git push origin main
```

### If you get "authentication failed":

1. Create Personal Access Token (as shown above)
2. Use token as password when prompted
3. Or use: `git config credential.helper wincred` to store it

---

## Change Your Password (Important!)

Since your password was shared, change it at: https://github.com/settings/security

1. Go to Settings → Password
2. Enter current password
3. Enter new password
4. Confirm new password
5. Click "Update password"

---

## Secure Authentication Methods

### Option 1: Personal Access Token (Recommended)
- Create at: https://github.com/settings/tokens
- Use token as password in Git operations
- Can revoke anytime if compromised

### Option 2: SSH Keys (Most Secure)
```powershell
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: https://github.com/settings/keys
# Copy public key and add as SSH key

# Change remote URL to SSH
git remote set-url origin git@github.com:alexyalensky/chemipal-app.git
```

### Option 3: GitHub CLI
```powershell
gh auth login
# Follow prompts to authenticate
```

---

## Next Steps

1. **Change your GitHub password immediately**
2. **Create Personal Access Token** at https://github.com/settings/tokens
3. **Push your code** using the token
4. **Set up credential helper** to avoid re-entering credentials

You're all set with Git! 🎉

