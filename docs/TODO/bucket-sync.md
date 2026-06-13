# GCS Bucket Synchronization (Future Feature)

## Overview
Implement manual synchronization (push/pull) of the ChromaDB index between the local server and a GCS bucket to ensure persistence and multi-instance data consistency.

## Requirements
- UI input field for GCS bucket name.
- Backend endpoint to validate bucket accessibility.
- Manual 'Pull' endpoint: Download index from GCS, unzip, and overwrite local ChromaDB path.
- Manual 'Push' endpoint: Zip local ChromaDB path and upload to GCS.
- Status feedback (Toasts) for success/failure.

## Implementation Details (Previously implemented, needs re-integration)
- Backend routes (FastAPI):
    - `GET /check-bucket/{bucket_name}`
    - `POST /sync/pull` (uses `Form` for bucket name)
    - `POST /sync/push` (uses `Form` for bucket name)
- Frontend:
    - Update `base.html` for inputs/buttons.
    - `app.js` logic for `fetch` calls, toast notifications, and `localStorage` persistence of bucket name.
- Dependency: `google-cloud-storage` python library.

## Issues Identified
- URL encoding issues when passing bucket names with `gs://` prefix.
- Need to ensure `storage` is correctly imported in backend modules.
