# Render Deployment Guide for ApexFinance & SME Suite

This guide explains how to deploy your accounting tool and inventory suite to **Render** so that it works seamlessly and is publicly accessible.

---

## What Was Fixed
1. **Dynamic Path Resolution**: Removed local Windows path `c:\Users\salom\ide.tool\index.html` and replaced it with dynamic relative path resolution (`BASE_DIR`).
2. **Static File & Tool Serving**: Added support for serving all tools (`index.html`, `zerainventory.html`, `newinventory.html`, `thirdtool.html`) and static assets (`.css`, `.js`, `.png`, `.svg`, `.json`).
3. **Dynamic `$PORT` Binding**: Configured Python web backend to bind to `0.0.0.0` and listen to Render's dynamic `$PORT`.
4. **Root Dependency Management**: Created root `requirements.txt`, `Procfile`, and `render.yaml` for Render auto-detection.

---

## Step-by-Step Deployment Instructions

### Method A: Blueprint Auto-Deploy (Recommended)
1. Commit and push all project files to your GitHub / GitLab repository:
   ```bash
   git add .
   git commit -m "Fix Render deployment path, port binding and static routing"
   git push origin main
   ```
2. Log into your [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** -> **Blueprint**.
4. Select your repository. Render will automatically read `render.yaml` and configure the Web Service for you.
5. Click **Apply**.

---

### Method B: Manual Web Service Setup
If creating a Manual Web Service on Render:
- **Name**: `apex-finance-suite`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python backend/app.py` (or `python server.py`)

---

## Verifying Deployment
Once Render finishes building:
1. Open your Render Web Service URL (e.g., `https://apex-finance-suite.onrender.com`).
2. You will see the **ApexFinance Enterprise Suite** interface immediately.
3. Access sub-tools directly or via the sidebar menu:
   - **Main Accounting Dashboard**: `/` or `/index.html`
   - **Zera Inventory ERP**: `/zerainventory.html`
   - **Nexus Supply Chain**: `/newinventory.html`
   - **Financial Accounting Engine**: `/thirdtool.html`
   - **API Health Endpoint**: `/api/status`
