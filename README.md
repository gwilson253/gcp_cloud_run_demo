# GCP Cloud Run Service Demo
This demo shows how to set up a Google Cloud Run __service__, with scheduled triggers from Google Cloud Scheduler, which trigger a toy python FastAPI app to fetch a random cat fact and load it into a text file in a Google Cloud Bucket.

Note that the Cloud Run Service expects to be triggered by an HPPT request. What I was really after was a Cloud Service Job, which doesn't require a WSGI / ASGI, and can just run as a simple python job. I'm keeping this around, as there are other patterns where using Cloud Run to service API requests will be useful.

# gcloud Command Reference & Setup
## Enable required cloud services
These services are required for the app to run. The following command enables them for the Google Cloud project.

```
gcloud services enable cloudbuild.googleapis.com \
    run.googleapis.com \
    cloudscheduler.googleapis.com \
    artifactregistry.googleapis.com \
    logging.googleapis.com
```

## Create a container registry
The Container Registry is where build artifacts for your project will be stored. 
```
gcloud artifacts repositories create <my-repo> \
    --repository-format=Docker \
    --location=us-west1
```

## Build app
This command takes the `Dockerfile` in this folder and creates a build artifact that is stored in the Container Registry.

```
gcloud builds submit --tag <my-repo>/$(gcloud config get-value project)/<my-job>`
```

## Google Cloud Bucket
### Create the target bucket
```
gcloud storage buckets create gs://<my-bucket> \
    --location=us-west1
```

### Add Permission to create objects in bucket for Cloud Run service account
Here we're assigning the `storage.objectCreator` role to the Google Cloud Run service account. 
```
gcloud storage buckets add-iam-policy-binding gs://<my-bucket> \
    --member=serviceAccount:<project-id-number>-compute@developer.gserviceaccount.com \
    --role=roles/storage.objectCreator
```

## Deploy Cloud Run Service app 
```
gcloud run deploy <my-job-service> \
    --image my-repo/$(gcloud config get-value project)/my-job \
    --platform managed \
    --region us-west1 \
    --allow-unauthenticated \
    --set-env-vars GCS_BUCKET=<my-bucket>
```

## Create Cloud Scheduler job
```
gcloud scheduler jobs create http my-scheduled-job \
    --location "us-west1" \
    --schedule "*/5 * * * *" \
    --uri "<my-job-uri>" \
    --http-method=POST \
    --oidc-service-account-email "<cloud-scheduler-invoker-email>"
```

## Misc useful gcloud commands
### Fetch IAM Policies
`gcloud projects get-iam-policy $(gcloud config get-value project) --flatten="bindings[].members" --format="table(bindings.members)"`

### Update the bucket env var
```
gcloud run services update <my-job-service> \
    --set-env-vars GCS_BUCKET=<my-bucket>
```

### Fetch Cloud Run Job URI
`gcloud run services describe <my-job-service> --region=us-west1 --format="value(status.url)"`

### Update Cloud Scheduler target URI
```
gcloud scheduler jobs update http <my-scheduled-job> \
    --uri "<CORRECT_CLOUD_RUN_URL>"
```