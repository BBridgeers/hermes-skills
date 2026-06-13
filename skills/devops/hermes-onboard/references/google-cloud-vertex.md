# Google Cloud Vertex AI Setup

Connect Hermes to Google Cloud Vertex AI for production-tier Gemini/Imagen/Veo models with no rate limits.

## Prerequisites

- Google Cloud project with billing enabled
- Vertex AI API enabled in the project

## Step 1: Install gcloud CLI

```bash
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee /etc/apt/sources.list.d/google-cloud-sdk.list
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
apt-get update && apt-get install -y google-cloud-cli
```

## Step 2: Authenticate

```bash
gcloud auth login                    # CLI auth (opens browser, paste verification code)
gcloud auth application-default login # SDK auth (for Python libraries)
```

## Step 3: Set project

```bash
gcloud projects list                                  # find your project ID
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

## Step 4: Install Python SDK

```bash
pip install --break-system-packages google-cloud-aiplatform Pillow
```

## Step 5: Verify

```bash
gcloud services list --enabled | grep aiplatform
```

## Image Generation (Imagen)

```python
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

vertexai.init(project="YOUR_PROJECT_ID")
model = ImageGenerationModel.from_pretrained("imagen-4.0-generate-001")
images = model.generate_images(
    prompt="a beautiful sunset over mountains",
    number_of_images=1,
    aspect_ratio="1:1",
)
images[0].save("output.png")
```

## Pitfalls

- **Service Account vs User Auth**: `gcloud auth login` logs in as a user (full permissions). Service accounts need IAM role `Vertex AI User`.
- **Billing required**: Vertex AI is NOT free. Imagen images cost ~$0.02-0.05 each depending on resolution.
- **Rate limits**: Vertex AI has much higher quotas than AI Studio free tier. Check quotas at console.cloud.google.com/apis/api/aiplatform.googleapis.com/quotas.
- **Project selection**: `gcloud config set project` must match a project with Vertex AI API enabled and billing active.
- **ADC quota project**: Without `gcloud auth application-default set-quota-project`, ADC may fail with "quota exceeded" errors.
