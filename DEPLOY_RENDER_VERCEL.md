# Deploy Free: Render Backend + Vercel Frontend

This setup keeps your backend off your machine and makes React the public UI.

## 1) Deploy backend on Render (free)

1. Push this repo to GitHub.
2. In Render: **New +** -> **Blueprint** -> connect repo.
3. Render will detect `render.yaml` and create service `aqi-predictor-api`.
4. In Render service env vars, set:
   - `OPENWEATHER_API_KEY=<your_key>`
   - `AQI_ENABLE_TENSORFLOW=0`
5. Deploy and copy your backend URL, e.g.:
   - `https://aqi-predictor-api.onrender.com`
6. Verify:
   - `https://aqi-predictor-api.onrender.com/api/health`

Notes:
- Free Render services sleep when idle and cold-start on first request.
- API build uses `requirements-api.txt` (lighter than full project requirements).

## 2) Deploy frontend on Vercel (free)

1. In Vercel: **Add New Project** -> import same repo.
2. Set **Root Directory** to `frontend`.
3. Framework preset: `Create React App` (auto-detected).
4. Add environment variable:
   - `REACT_APP_API_URL=https://aqi-predictor-api.onrender.com`
5. Deploy.

## 3) Confirm end-to-end

- Open your Vercel URL.
- Select a city and verify:
  - Current AQI loads from Render backend.
  - Predictions load from Render backend.

## 4) If frontend still points wrong

Recheck Vercel env var and trigger **Redeploy**.
`REACT_APP_API_URL` is build-time for CRA, so it must exist before build.
