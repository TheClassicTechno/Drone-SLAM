# Deploy webhook + Vercel so live transcript works on the dashboard

Follow these steps so the **Vercel dashboard** shows the **live transcript** (and Vapi can reach your webhook).

---

## 1. Deploy the webhook server (choose one)

### Option A: Railway

1. Go to [railway.app](https://railway.app) and sign in (e.g. with GitHub).
2. **New Project** → **Deploy from GitHub repo** → select your `Drone-SLAM` repo.
3. After the repo is connected, click the new service → **Settings**:
   - **Root Directory**: set to `voice_agent` (so Railway runs the webhook from that folder).
   - **Start Command**: leave empty (the `Procfile` in `voice_agent` runs `uvicorn`).
4. **Variables** tab → add (at minimum):
   - `CORS_ORIGINS` = `https://drone-slam-git-main-julis-projects-7b0310a2.vercel.app`  
     (use your exact Vercel dashboard URL; add more origins comma-separated if needed)
   - Copy from your local `.env`: `VAPI_API_KEY`, and any of `ZOOM_WEBHOOK_URL`, `ZOOM_API_KEY`, `ZOOM_API_SECRET` if you use Zoom.
5. **Deploy** (or trigger redeploy). When it’s up, open **Settings** → **Networking** → **Generate Domain**. Copy the URL (e.g. `https://your-app.up.railway.app`).  
   → This is your **backend URL**. Use it in step 2 and 3.

### Option B: Render

**Either use the Blueprint (easiest):**  
**New** → **Blueprint** → connect `TheClassicTechno/Drone-SLAM`. Render will use `render.yaml` and create the service. Then open the service → **Environment** and add the env vars below.

**Or create the service manually** (e.g. you’re on “New Web Service”):

Fill the form like this:

| Field | Value |
|-------|--------|
| **Name** | `drone-slam-webhook` (or any name you like) |
| **Project** | (optional) e.g. “My project” |
| **Environment** | Production |
| **Language** | **Python** (do **not** use Docker) |
| **Branch** | `main` |
| **Region** | Oregon (US West) or your preference |
| **Root Directory** | `voice_agent` |
| **Instance Type** | Free (or Starter if you want no spin-down) |

You must set **Build** and **Start** (often under “Advanced” or in a second step):

| Field | Value |
|-------|--------|
| **Build Command** | `cd voice_agent && pip install -r requirements.txt` |
| **Start Command** | `cd voice_agent && uvicorn webhook_server:app --host 0.0.0.0 --port $PORT` |

**Environment Variables** — click “Add Environment Variable” for each:

| NAME | VALUE |
|------|--------|
| `CORS_ORIGINS` | `https://drone-slam-git-main-julis-projects-7b0310a2.vercel.app` |
| `VAPI_API_KEY` | (paste from your local `voice_agent/.env`) |

If you use Zoom notifications, add:

| NAME | VALUE |
|------|--------|
| `ZOOM_WEBHOOK_URL` | (from your .env) |
| `ZOOM_API_KEY` | (from your .env) |
| `ZOOM_API_SECRET` | (from your .env) |

Then click **Deploy web service**. When it’s live, copy the service URL (e.g. `https://drone-slam-webhook.onrender.com`) — that’s your **backend URL** for step 2 and 3.

---

## 2. Point Vercel at the backend

1. Open [Vercel Dashboard](https://vercel.com) → your project (the one that serves the MedWing/dashboard frontend).
2. **Settings** → **Environment Variables**.
3. Add:
   - **Name**: `VITE_API_URL`  
   - **Value**: your backend URL from step 1, **no trailing slash**  
     (e.g. `https://your-app.up.railway.app` or `https://drone-slam-webhook.onrender.com`)
   - Apply to **Production** (and Preview if you want).
4. **Redeploy** the frontend (Deployments → … → Redeploy) so the new env is baked in.

---

## 3. Point Vapi at the backend

1. In [Vapi Dashboard](https://dashboard.vapi.ai) (or wherever you configured your assistant), set the **Webhook URL** to:
   - `https://YOUR-BACKEND-URL/vapi-webhook`  
   (same base URL as `VITE_API_URL`, path `/vapi-webhook`).
2. Save. New calls will hit the deployed server; the dashboard will get live transcript from `/live-transcript` on that same URL.

---

## Checklist (after backend is live)

| Step | What | Where |
|------|------|--------|
| 1 | Set `CORS_ORIGINS` = your Vercel app URL | Render → your service → Environment |
| 2 | Set `VITE_API_URL` = backend URL (no slash) | Vercel → Settings → Environment Variables |
| 3 | Redeploy Vercel frontend | Vercel → Deployments → Redeploy |
| 4 | Set Vapi webhook URL to `https://YOUR-BACKEND-URL/vapi-webhook` | Vapi dashboard |

After this, the Vercel dashboard will connect to your deployed backend’s `/live-transcript` and show the transcript there.

**Your backend URL:** `https://drone-slam.onrender.com`

---

## Troubleshooting: CORS / "localhost:8000" from Vercel

If you see:
- *"Access to resource at 'http://localhost:8000/live-transcript' from origin 'https://drone-slam.vercel.app' has been blocked by CORS"*
- Or the dashboard shows "Connecting..." and never "Live Connected"

then either the frontend is still using localhost, or the backend is not allowing your Vercel origin.

**1. Frontend must use Render, not localhost**

- In **Vercel** → **Settings** → **Environment Variables**, set:
  - `VITE_API_URL` = `https://drone-slam.onrender.com` (no trailing slash).
- **Redeploy**: **Deployments** → **⋯** on latest → **Redeploy**.  
  Vite bakes `VITE_API_URL` into the build; a new deployment is required for the change to take effect.

**2. Backend must allow your Vercel origin**

- In **Render** → your **Drone-SLAM** service → **Environment**:
  - `CORS_ORIGINS` = `https://drone-slam.vercel.app`  
  (use your real Vercel URL; add multiple origins comma-separated if you have several, e.g. preview URLs).
- **Save** so Render redeploys. Then reload the Vercel dashboard and try again.

---

## Transcript not on website? (webhooks going to local)

If the transcript appears in your **terminal** (e.g. `tail -f /tmp/webhook_server_new.log`) but **not** on https://drone-slam.vercel.app/dashboard, Vapi is still sending webhooks to your **local** server (or ngrok), not to Render. The dashboard only shows what **Render** receives.

**Fix (do in order):**

1. **Point Vapi at Render**
   ```bash
   cd voice_agent
   python set_vapi_server_url.py
   ```
   (Uses `VAPI_API_KEY` and `VAPI_PHONE_NUMBER_ID` from `.env`.)

2. **Stop your local webhook server** so only Render receives webhooks:
   - **Option A:** In the terminal where you ran `python webhook_server.py`, press **Ctrl+C**.
   - **Option B:** Run from repo root:
     ```bash
     cd voice_agent && bash stop_local_webhook.sh
     ```
   - **Option C:** Stop ngrok if you use it (so the old public URL no longer reaches your machine).

3. **Test**
   - Open https://drone-slam.vercel.app/dashboard (should show **Live Connected**).
   - Call your Vapi number. The transcript should appear on the dashboard.
   - In **Render** → your service → **Logs**, you should see `Webhook received: conversation-update` and `POST /vapi-webhook HTTP/1.1` 200.

4. **Deploy latest code to Render** (so the fork has the latest webhook logic):
   - Push your branch to **marianaisaw/Drone-SLAM**, then update the **TheClassicTechno/Drone-SLAM** fork (e.g. Sync fork or push to that remote). Render will redeploy from the fork.
