import os
import requests
import logging
from fastapi import FastAPI
from google.cloud import storage

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Public API URL (Example: Fetch random cat facts)
DATA_SOURCE_URL = "https://catfact.ninja/fact"

# Google Cloud Storage bucket name (set via environment variable)
BUCKET_NAME = os.getenv("GCS_BUCKET", "your-default-bucket")

def fetch_data():
    """Fetch data from a public API."""
    response = requests.get(DATA_SOURCE_URL)
    response.raise_for_status()
    return response.json()["fact"]

def upload_to_gcs(data):
    """Upload data to Google Cloud Storage."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob("data.txt")
    blob.upload_from_string(data)
    logging.info(f"Data uploaded to gs://{BUCKET_NAME}/data.txt")

@app.post("/")
async def run_job():
    """Cloud Run entrypoint for the scheduled job."""
    logging.info("Job started...")
    try:
        data = fetch_data()
        upload_to_gcs(data)
        return {"status": "success", "data": data}
    except Exception as e:
        logging.error(f"Error: {e}")
        return {"status": "error", "message": str(e)}