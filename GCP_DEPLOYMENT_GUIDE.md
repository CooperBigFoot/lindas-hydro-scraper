# Google Cloud Functions Deployment Guide for LINDAS Hydro Scraper

## Project Information

### 1. **Programming Language and Version** ⚙️
- **Language:** Python
- **Version:** 3.12+ (as specified in `pyproject.toml`)

### 2. **Dependencies and Package Management** 📦
This project uses **uv** as the package manager, but for Google Cloud Functions deployment, we need to generate a `requirements.txt` file.

**Current dependencies:**
- pandas>=2.2.0
- python-dotenv>=1.0.0
- SPARQLWrapper>=2.0.0
- pydantic>=2.5.0
- pydantic-settings>=2.1.0

**To generate requirements.txt for GCF:**
```bash
uv pip compile pyproject.toml -o requirements.txt
```

### 3. **Code Structure and Entrypoint** 入口
- **Entry function name:** `main`
- **Entry file:** `src/lindas_hydro_scraper/main.py`
- **Function signature:** `main() -> None`

**Note:** For Google Cloud Functions, we'll need to create a wrapper function that GCF can invoke, as the current `main()` function doesn't accept the required `(request)` parameter for HTTP-triggered functions.

### 4. **Environment Variables** 🔑
The application uses the following environment variables (all have defaults):

- `SPARQL_ENDPOINT` - SPARQL endpoint URL (default: https://ld.admin.ch/query)
- `SPARQL_BASE_URL` - Base URL for LINDAS hydro data (default: https://environment.ld.admin.ch/foen/hydro)
- `SITE_CODES` - Comma-separated list of station codes to scrape
- `PARAMETERS` - Comma-separated list of parameters to collect
- `HYDRO_DATA_DIR` - Directory for output files (default: ./data)
- `OUTPUT_FILENAME` - Output CSV filename (default: lindas_hydro_data.csv)
- `RETRY_MAX_ATTEMPTS` - Maximum retry attempts (default: 3)
- `RETRY_DELAY` - Initial retry delay in seconds (default: 2.0)

### 5. **Network and Permissions** 🌐

**External Network Access Required:**
- The function makes HTTPS requests to `https://ld.admin.ch/query` (SPARQL endpoint)
- No VPC access required

**Google Cloud Service Permissions:**
- **Cloud Storage:** If you want to save the scraped CSV files to Google Cloud Storage, the function will need:
  - `storage.objects.create` permission
  - `storage.objects.delete` permission (if overwriting files)
  - Service account with `Storage Object Creator` role

**No other GCP services are currently used by the application.**

## Deployment Steps

### Step 1: Prepare the Code for GCF

1. Create a new file `main_gcf.py` in the root directory with a GCF-compatible wrapper:

```python
import functions_framework
from src.lindas_hydro_scraper.main import main as scraper_main

@functions_framework.http
def main(request):
    """HTTP Cloud Function entry point."""
    try:
        scraper_main()
        return {"status": "success", "message": "Scraping completed successfully"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
```

2. Generate `requirements.txt`:
```bash
uv pip compile pyproject.toml -o requirements.txt
```

### Step 2: Deploy to Google Cloud Functions

```bash
gcloud functions deploy lindas-hydro-scraper \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point main \
  --source . \
  --timeout 540s \
  --memory 512MB \
  --set-env-vars SPARQL_ENDPOINT=https://ld.admin.ch/query,SITE_CODES="2044,2112,2491,2355"
```

### Step 3: Optional - Save to Cloud Storage

If you want to save the CSV output to Cloud Storage instead of local filesystem:

1. Grant your function's service account the `Storage Object Creator` role:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/storage.objectCreator"
```

2. Modify the code to upload to GCS after scraping completes.

## Important Considerations

1. **Timeout:** The default timeout for Cloud Functions is 60s. This scraper might take longer depending on the number of sites. Consider increasing the timeout (max 540s for HTTP functions).

2. **Memory:** Start with 512MB and adjust based on the data volume.

3. **Cold Starts:** The first invocation might be slower due to cold start. Consider using Cloud Scheduler to keep the function warm.

4. **Output Storage:** The current implementation saves to local filesystem, which is ephemeral in Cloud Functions. Consider modifying to save to Cloud Storage for persistence.

5. **Logging:** The application uses Python's logging module, which integrates well with Cloud Functions' logging.