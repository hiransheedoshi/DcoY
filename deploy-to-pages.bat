@echo off
echo ========================================
echo DcoY Deployment Script
echo ========================================
echo.
echo This will build and deploy your app to Cloudflare Pages
echo.

cd frontend

echo [1/4] Installing dependencies...
call npm install

echo.
echo [2/4] Building the application...
call npm run build

echo.
echo [3/4] Installing Wrangler CLI...
call npm install -g wrangler

echo.
echo [4/4] Deploying to Cloudflare Pages...
echo.
echo Please login to Cloudflare when prompted...
call wrangler pages deploy dist --project-name=dcoy

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Your site should be live at: https://dcoy.pages.dev
echo.
pause
