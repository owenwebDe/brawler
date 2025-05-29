# 🐙 GitHub Pages Complete Setup Guide

## 🚀 Step-by-Step GitHub Pages Deployment

### Step 1: Create GitHub Repository

1. **Go to GitHub.com** and sign in (or create account)
2. **Click "New repository"** (green button)
3. **Repository name:** `fighting-game` (or your preferred name)
4. **Make it Public** ✅
5. **Add README** ✅
6. **Click "Create repository"**

### Step 2: Prepare Your Files

```bash
# Navigate to your brawler folder
cd "C:\Users\Admin\Desktop\New folder\brawler"

# Create GitHub deployment folder
mkdir github-deploy
cd github-deploy

# Copy auto-detection page to root
copy ..\index.html index.html

# Copy PC version (from build/web)
mkdir pc
xcopy "..\pc\build\web\*" pc\ /E /H /C /I

# Copy mobile version (from build/web)
mkdir mobile
xcopy "..\mobile\build\web\*" mobile\ /E /H /C /I
```

### Step 3: Upload to GitHub

#### Option A: GitHub Desktop (Easiest)

1. **Download GitHub Desktop** from [desktop.github.com](https://desktop.github.com)
2. **Clone your repository:**
   - File → Clone repository
   - Choose your `fighting-game` repo
3. **Copy files:**
   - Copy everything from `github-deploy` to your cloned repo folder
4. **Commit and push:**
   - Add commit message: "Deploy fighting game"
   - Click "Commit to main"
   - Click "Push origin"

#### Option B: Command Line

```bash
# In your github-deploy folder
git init
git add .
git commit -m "Deploy fighting game with auto-detection"
git branch -M main
git remote add origin https://github.com/yourusername/fighting-game.git
git push -u origin main
```

### Step 4: Enable GitHub Pages

1. **Go to your repository** on GitHub.com
2. **Click "Settings"** tab
3. **Scroll to "Pages"** section (left sidebar)
4. **Source:** "Deploy from a branch"
5. **Branch:** "main"
6. **Folder:** "/ (root)"
7. **Click "Save"**

### Step 5: Wait and Access

- **Wait 2-5 minutes** for deployment
- **Your game will be live at:**
  ```
  https://yourusername.github.io/fighting-game/
  ```

## 📁 Required GitHub Folder Structure

Your repository should look like this:

```
fighting-game/                   (your GitHub repo)
├── README.md                   (auto-generated)
├── index.html                  (auto-detection page)
├── pc/                        (PC version)
│   ├── index.html             (from pc/build/web/index.html)
│   ├── main.py               (from pc/build/web/main.py)
│   ├── assets/               (from pc/build/web/assets/)
│   │   ├── images/
│   │   ├── audio/
│   │   └── fonts/
│   ├── archives/             (from pc/build/web/archives/)
│   └── (all other build files)
└── mobile/                   (mobile version)
    ├── index.html            (from mobile/build/web/index.html)
    ├── main_mobile.py        (from mobile/build/web/main_mobile.py)
    ├── assets/               (from mobile/build/web/assets/)
    │   ├── images/
    │   ├── audio/
    │   └── fonts/
    ├── archives/             (from mobile/build/web/archives/)
    └── (all other build files)
```

## 🔧 Troubleshooting "Page Not Found"

### Check 1: Correct Repository Settings

- Repository must be **Public**
- Pages source must be **"main" branch**
- Pages folder must be **"/ (root)"**

### Check 2: File Structure

Your `index.html` must be in the **root** of your repository:

```
✅ Correct: fighting-game/index.html
❌ Wrong: fighting-game/github-deploy/index.html
```

### Check 3: Wait Time

- GitHub Pages takes **2-10 minutes** to deploy
- Check the "Actions" tab to see deployment status
- Green checkmark = deployed successfully

### Check 4: URL Format

Make sure you're using the correct URL:

```
✅ Correct: https://yourusername.github.io/fighting-game/
❌ Wrong: https://github.com/yourusername/fighting-game/
```

## 🎯 Complete Setup Script

Save this as `deploy-to-github.bat`:

```batch
@echo off
echo Setting up GitHub Pages deployment...

cd "C:\Users\Admin\Desktop\New folder\brawler"

REM Create GitHub deployment folder
if exist github-deploy rmdir /s /q github-deploy
mkdir github-deploy
cd github-deploy

REM Copy auto-detection page
copy ..\index.html index.html
echo ✅ Copied auto-detection page

REM Copy PC version
mkdir pc
xcopy "..\pc\build\web\*" pc\ /E /H /C /I /Q
echo ✅ Copied PC version

REM Copy mobile version
mkdir mobile
xcopy "..\mobile\build\web\*" mobile\ /E /H /C /I /Q
echo ✅ Copied mobile version

REM Initialize git
git init
git add .
git commit -m "Deploy fighting game with auto-detection"
git branch -M main

echo.
echo ✅ Files ready for GitHub!
echo ✅ Next steps:
echo    1. Create repository on GitHub.com
echo    2. Run: git remote add origin https://github.com/yourusername/fighting-game.git
echo    3. Run: git push -u origin main
echo    4. Enable Pages in repository settings
echo.
pause
```

## 🌐 Testing Your Deployment

### After GitHub Pages is enabled:

1. **Visit your URL:** `https://yourusername.github.io/fighting-game/`

2. **Test auto-detection:**

   - Desktop browser → Should redirect to `/pc/`
   - Mobile browser → Should redirect to `/mobile/`

3. **Test direct access:**
   - PC version: `https://yourusername.github.io/fighting-game/pc/`
   - Mobile version: `https://yourusername.github.io/fighting-game/mobile/`

## 🔄 Updating Your Live Game

When you make changes:

```bash
# Make your changes and rebuild
cd pc && pygbag main.py
cd ../mobile && pygbag main_mobile.py

# Update GitHub deployment
cd ../github-deploy
xcopy "..\pc\build\web\*" pc\ /E /H /C /I /Y
xcopy "..\mobile\build\web\*" mobile\ /E /H /C /I /Y

# Push to GitHub
git add .
git commit -m "Update game"
git push origin main

# Live in 2-3 minutes!
```

## 💡 Pro Tips for GitHub Pages

### Custom Domain (Optional):

1. **Buy domain:** `yourgame.com`
2. **Add CNAME file** to repository root:
   ```
   yourgame.com
   ```
3. **Configure DNS** at domain provider

### SEO Optimization:

Add to your `index.html`:

```html
<meta name="description" content="Epic fighting game - Play in browser" />
<meta name="author" content="Your Name" />
<link rel="canonical" href="https://yourusername.github.io/fighting-game/" />
```

### Analytics:

Add Google Analytics to track visitors:

```html
<!-- Google Analytics -->
<script
  async
  src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
></script>
```

## 🎮 Your Live Game Features

Once deployed, your game will have:

- ✅ **Professional URL:** `yourusername.github.io/fighting-game`
- ✅ **Auto device detection**
- ✅ **Mobile touch controls**
- ✅ **Desktop keyboard controls**
- ✅ **Fast global loading**
- ✅ **Free forever hosting**
- ✅ **Version control**
- ✅ **Easy updates**

**GitHub Pages is perfect for pygame web games** - it handles the Python runtime files better than most other platforms!
