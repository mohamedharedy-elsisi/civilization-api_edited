---
title: Egyptian Artifact Detector
emoji: 🏺
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 6.26.0
python_version: "3.12"
app_file: app.py
---

# AI Inference Service

This directory is a standalone Hugging Face Gradio Space. Deploy the **contents** of this directory to a new Space; do not point Vercel at it.

The service exposes a browser UI, the Gradio queue API at `/gradio_api/call/predict`, a compatibility REST endpoint at `POST /api/predict`, and `GET /health`. The REST endpoint accepts multipart form field `image`, matching the original Flask route.

## Model setup

The 22.5 MB `weights/best.pt` file is intentionally not copied into this service or its Git history. Keep it in a private Hugging Face Model repository, or provide it as a local `MODEL_PATH` when running the service yourself. Hugging Face currently lists 100 GB of private Hub storage for free accounts, so this file is within the stated free storage allowance. The Hugging Face Space downloads it at startup.

Add these settings in **Space Settings → Variables and secrets**:

| Name | Type | Value |
| --- | --- | --- |
| `HF_MODEL_REPO_ID` | Variable | The model repository containing `best.pt`, such as your own private model repository ID |
| `HF_MODEL_FILENAME` | Variable | `best.pt` |
| `HF_MODEL_REVISION` | Variable | A branch, tag, or immutable commit SHA; use a commit SHA for reproducible deployment |
| `HF_TOKEN` | Secret | Read-only token for the private model repository |
| `CIVILIZATION_API_BASE_URL` | Variable | `https://civilization-api.vercel.app` |
| `USE_ZERO_GPU` | Variable | `true` only when ZeroGPU hardware is selected; otherwise `false` |
| `CORS_ALLOW_ORIGINS` | Variable | Comma-separated exact origins if calling from Flutter Web; leave empty for mobile-only clients |
| `MAX_UPLOAD_BYTES` | Variable | Optional; defaults to `10485760` (10 MiB) |

`MODEL_PATH` can be used instead of the Hub settings. It takes precedence when set. Never put the Hub token in a public variable or in Flutter code.

## Hosting notes

The service supports Hugging Face ZeroGPU and CPU Basic. ZeroGPU is currently the only no-monthly-plan path for hosting a Gradio Space on an eligible free personal account. The model is placed on CUDA at startup and prediction requests use the ZeroGPU decorator when `USE_ZERO_GPU=true`. Hugging Face currently limits anonymous ZeroGPU callers to a shared pool of 2 GPU minutes per day; authenticated free users get 5 minutes per day, but a Hugging Face token must not be embedded in a distributed Flutter app. Queue availability and daily limits can therefore make the free option unsuitable for a public app.

CPU Basic has no hourly compute charge, but creating a Gradio Space on compute currently requires Hugging Face PRO ($9/month). It provides 2 vCPU and 16 GB RAM, sleeps after inactivity, and may have slower inference than GPU hardware. Confirm current account and hardware rules before deployment.

The Space starts without a model if the repository settings are missing or invalid. In that state `/health` returns HTTP 503 with `model_loaded: false`; the client receives a generic service error. Model paths and stack traces are written only to server logs. Hub model downloads and service restarts can make the first request take longer than subsequent requests.

## Local run

From this directory, set `MODEL_PATH` to the existing `best.pt` file or configure the Hugging Face model repository variables above. Then install `requirements.txt` and run:

```powershell
$env:MODEL_PATH = '..\weights\best.pt'
python app.py
```

The local server listens on port 7860 by default. Set `USE_ZERO_GPU=false` for local CPU inference.

## API formats

### Flutter REST compatibility endpoint

Set Flutter's `AI_API_BASE_URL` to the Space's actual public base URL (the `https://<space-subdomain>.hf.space` value shown in Space settings). The client posts one file as multipart field `image` to `/api/predict`:

```text
POST https://<space-subdomain>.hf.space/api/predict
Content-Type: multipart/form-data
field: image=<image file>
```

A detection returns the same fields as the old service:

```json
{
  "success": true,
  "prediction": {"class": "Artifact class", "confidence": 0.91},
  "artifact": {"name": "Artifact class"}
}
```

`artifact` is the matching full object from the Data API, or `null` if the Data API is unavailable or has no exact class-name match. No detection returns HTTP 200 with `{"success": false, "message": "No artifact detected"}`. Missing, invalid, and oversized uploads return a clear `error` and an HTTP 4xx status. A model that is not ready returns HTTP 503.

### Native Gradio queue API

The Gradio interface is also exposed as `/gradio_api/call/predict`. Gradio file inputs use its upload endpoint first, then submit the returned file path to the queue API. Check `/gradio_api/openapi.json` or the Space's **Use via API** page for the live schema. This native API returns a queued event and streams the result; the REST endpoint above returns the response directly and is the interface used by Flutter.

### Health

`GET /health` reports readiness without exposing file paths, repository IDs, tokens, or stack traces. A 200 response means the model loaded. A 503 response means the Space is running but inference is unavailable.

## Deploy

1. Create a new **Gradio Space** and choose ZeroGPU on an eligible free account, or CPU Basic if the account has a plan that permits compute Spaces. Do not use a Static Space.
2. Upload or push the contents of `ai_service/` as the Space repository root. The included `README.md` contains the Space runtime metadata.
3. Upload the existing `weights/best.pt` from the original project to a separate private Hugging Face Model repository. Do not add it to the Space or application Git repository.
4. Configure the variables and secret from the table above. For ZeroGPU, select ZeroGPU hardware and set `USE_ZERO_GPU=true`; for CPU Basic set it to `false`.
5. Wait for the Space to finish building and check its logs for model-load errors.
6. Call `/health`, upload an actual artifact image to `/api/predict`, and verify the JSON contract before setting `AI_API_BASE_URL` in Flutter.

The app code is prepared for deployment, but no Space was created or deployed from this workspace.
