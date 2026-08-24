# Deploying ZENORA ACCOUNTING & FINANCE on Render

Follow these steps to deploy **ZENORA ACCOUNTING & FINANCE** on Render cleanly without errors:

---

## 🛠️ Method 1: Using Blueprint (Recommended - Automatic Setup)

1. Go to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub repository (`zeracore2006-lgtm/Accounting-and-finance-tool`).
4. Render will automatically detect `render.yaml` and configure Python, dependencies, build command, and start command.
5. Click **Apply**. Render will build and deploy your live URL!

---

## ⚙️ Method 2: Manual Web Service Setup

If setting up manually in Render Dashboard:

1. Click **New +** → **Web Service**.
2. Connect your GitHub repository.
3. Configure the settings **EXACTLY** as follows:
   - **Name**: `zenora-accounting-finance`
   - **Language / Environment**: `Python 3` *(Do NOT select Node)*
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
4. Under **Advanced** → **Environment Variables**:
   - `PORT`: `10000`
5. Click **Create Web Service**.

---

## 💡 Why `error Couldn't find a package.json` Happened & How It's Fixed:
Render defaults to a **Node.js** environment if Language isn't explicitly set to **Python 3**. 
We have now added a `package.json` file to the repository so Render will build smoothly regardless of deployment mode!
