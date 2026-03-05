# Deploy React + API on a Cloud VM

This setup runs:
- React UI (public) on port `80` via Nginx
- Flask API on port `5001` (internal + optional host port)

The React app calls the API through `/api` (reverse proxy), so users only see one public URL.

## 1. Create a VM

Use any provider (AWS EC2, DigitalOcean, Hetzner, GCP) with:
- Ubuntu 22.04+
- 2 vCPU / 4 GB RAM minimum

Open firewall/security group:
- `80/tcp` (HTTP)
- `443/tcp` (HTTPS, if using Caddy/Nginx SSL)
- `22/tcp` (SSH)

## 2. Install Docker

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo systemctl enable --now docker
```

## 3. Clone project and configure env

```bash
git clone <your-repo-url>
cd aqi_project
cat > .env <<EOF
OPENWEATHER_API_KEY=your_openweather_key
AQI_ENABLE_TENSORFLOW=0
EOF
```

## 4. Build and run

```bash
docker compose up -d --build
docker compose ps
```

## 5. Verify

```bash
curl http://localhost:5001/api/health
curl http://localhost/
```

Open browser:
- `http://<YOUR_SERVER_IP>/`

## Optional: run Streamlit dashboard too

```bash
docker compose --profile dashboard up -d
```

Dashboard:
- `http://<YOUR_SERVER_IP>:8501`

## Recommended production hardening

- Put Caddy or Nginx in front for HTTPS + domain.
- Remove host exposure of API (`5001:5001`) if not needed publicly.
- Add monitoring/log shipping.
- Pin dependency versions for reproducible builds.
