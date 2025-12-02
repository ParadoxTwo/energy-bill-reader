# Deployment Guide

## Easiest Option: Railway

Railway is the easiest way to deploy this full-stack application because it:

- Supports both Node.js (Next.js) and Python (FastAPI) services
- Automatically provisions PostgreSQL and Redis
- Handles environment variables easily
- Can run multiple services (API, Worker, Frontend)

### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your repository and select this repo
4. Railway will create a service - this will be your backend API

### Step 2: Add Database Services

In your Railway project dashboard:

1. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
   - Railway will automatically create a `DATABASE_URL` environment variable
2. Click **"+ New"** → **"Database"** → **"Add Redis"**
   - Railway will automatically create a `REDIS_URL` environment variable

### Step 3: Configure Backend API Service

1. Click on your backend service (the one created from GitHub)
2. Go to **"Settings"** tab
3. **Important**: Leave **"Root Directory"** empty (project root)
   - The code uses relative imports that require running from the project root
4. Set **"Start Command"** to: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Railway should auto-detect this, but you can set it manually
5. Go to **"Variables"** tab and add:
   ```
   RQ_QUEUE_NAME=pdf-analysis
   UPLOAD_DIR=/tmp/uploads
   CORS_ORIGINS=http://localhost:3000,https://your-frontend-url.railway.app
   ```
   - Replace `https://your-frontend-url.railway.app` with your actual frontend URL (you'll get this after deploying the frontend)
   - `DATABASE_URL` and `REDIS_URL` are automatically added by Railway

### Step 4: Deploy Worker Service

1. In the same Railway project, click **"+ New"** → **"GitHub Repo"**
2. Select the same repository
3. In the service settings:
   - Leave **"Root Directory"** empty (project root)
   - Set **"Start Command"** to: `python -m backend.worker`
4. Go to **"Variables"** tab and add the same variables as the API service:
   ```
   RQ_QUEUE_NAME=pdf-analysis
   UPLOAD_DIR=/tmp/uploads
   ```
   - `DATABASE_URL` and `REDIS_URL` will be automatically available

### Step 5: Deploy Frontend (Next.js)

1. In Railway, click **"+ New"** → **"GitHub Repo"**
2. Select the same repository
3. Railway will auto-detect it's a Next.js project
4. Go to **"Variables"** tab and add:

   ```
   NEXT_PUBLIC_API_BASE_URL=<your-backend-api-url>
   ```

   - You can find your backend API URL in the backend service's **"Settings"** → **"Domains"** section
   - It will look like: `https://your-backend-service.railway.app`

5. After deployment, copy your frontend URL and update the `CORS_ORIGINS` in your backend service to include it.

### Step 6: Generate Domain (Optional)

For each service, you can generate a public domain:

1. Go to the service **"Settings"** tab
2. Click **"Generate Domain"** under the Domains section
3. This gives you a public URL like `https://your-service.railway.app`

## Alternative Options

### Option 2: Vercel (Frontend) + Railway (Backend)

Since Vercel is optimized for Next.js, you could:

1. Deploy frontend to [Vercel](https://vercel.com) (connects to GitHub, auto-deploys)
2. Deploy backend + worker to Railway (as described above)
3. Set `NEXT_PUBLIC_API_BASE_URL` in Vercel to your Railway backend URL

### Option 3: Render

Render is another easy option with similar features:

1. Create a **Web Service** for the FastAPI backend
2. Create a **Background Worker** for the RQ worker
3. Create a **Web Service** for Next.js (or use Static Site if you export it)
4. Add PostgreSQL and Redis from Render's templates

## Important Considerations

### File Storage

The current implementation stores files on disk (`uploads/` directory), which won't persist on most cloud platforms. You have two options:

1. **Use `/tmp` directory** (temporary, files will be lost on restart)
2. **Use object storage** (recommended for production):
   - AWS S3
   - Cloudflare R2
   - Railway's object storage

### CORS Configuration

Update the CORS origins in `backend/main.py` to include your production frontend URL.

### Database Migrations

The app currently creates tables automatically. For production, consider using Alembic for proper migrations.

## Troubleshooting

### Backend won't start / "uvicorn: command not found" / Python build conflicts

- Make sure `Root Directory` is **empty** (project root) in Railway settings
- Check that `nixpacks.toml` exists in the project root with the install commands
- Check that the Start Command is: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Check build logs to ensure `pip install -r backend/requirements.txt` ran successfully
- If you see conflicts about multiple Python environments, the `nixpacks.toml` should help Railway prioritize Python
- Verify that `backend/requirements.txt` and `backend/runtime.txt` exist
- Check that all environment variables are set correctly
- Verify PostgreSQL and Redis services are running

### Worker not processing jobs

- Ensure the worker service has the same environment variables as the API
- Check that `REDIS_URL` is correctly set
- Verify the worker service is running (check logs in Railway)

### CORS errors

- Make sure `CORS_ORIGINS` includes your frontend URL (no trailing slash)
- Check that the frontend's `NEXT_PUBLIC_API_BASE_URL` matches your backend URL

### File uploads not working

- Files in `/tmp` are temporary and will be lost on restart
- For production, consider using object storage (S3, Cloudflare R2, etc.)

## Quick Start Commands (Local Development)

After deployment, you can test locally with:

```bash
# Backend
cd backend
uvicorn main:app --reload

# Worker (in another terminal)
python -m backend.worker

# Frontend (in another terminal)
npm run dev
```
