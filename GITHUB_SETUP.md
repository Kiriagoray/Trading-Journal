# GitHub Setup Instructions

## Option 1: Create a NEW Repository on GitHub

1. **Go to GitHub and create a new repository:**
   - Visit: https://github.com/new
   - Repository name: `journalx` (or your preferred name)
   - Description: "Professional Django trading journal with AI features"
   - Choose: **Public** or **Private**
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

2. **Connect and push:**
   Run these commands (replace `YOUR_USERNAME` with your GitHub username):

   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/journalx.git
   git branch -M main
   git push -u origin main
   ```

## Option 2: Push to an EXISTING Repository

If you already created a repository on GitHub:

```bash
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

## Authentication

If you're asked for credentials:
- **Username**: Your GitHub username
- **Password**: Use a Personal Access Token (not your GitHub password)

### Creating a Personal Access Token:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name like "JournalX Project"
4. Select scopes: Check `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)
7. Use this token as your password when pushing

## Quick Command Summary

```bash
# Navigate to project
cd C:\Users\ADMIN\Videos\journal_project

# Add remote (replace with your details)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Rename branch to main (GitHub standard)
git branch -M main

# Push to GitHub
git push -u origin main
```

## After First Push

Your repository will be live at:
`https://github.com/YOUR_USERNAME/REPO_NAME`

You can share this URL with others or clone it on other machines!

