# Blob Storage Structure Migration Guide

## Issues Identified

### Issue 1: Extra "reports" folder at container level
- **Current Structure**: `resumes/`, `reports/`, `user@email.com/`, `guest/`
- **Expected Structure**: `resumes/` with all content inside

### Issue 2: User-specific containers instead of session-based paths
- **Current**: Files stored in `resumes-rajiv-ranjan-forasoftware-in` container
- **Expected**: Files stored in main `resumes` container with path structure `user@email.com/session_id/`

## Root Causes

1. **User Container Creation**: The `_get_or_create_user_container()` method creates separate containers per user
2. **Mixed Methods**: Code was using `upload_file_user()` instead of `upload_file_session()`
3. **Local Reports Folder**: Creating local "reports" folder that appears in blob listings

## Code Changes Applied

### Files Modified:
- `app/routers/resumes.py`: Changed to use `upload_file_session()`
- `app/routers/ranking.py`: Changed to use `upload_file_session()` and `list_blobs_session()`
- `app/routers/insights.py`: Changed to use `download_file_session()`
- `app/services/parser.py`: Changed to use session-based methods

### Key Changes:
```python
# Before (creates user containers)
blob_storage.upload_file_user(content, blob_name, user_id)
blob_storage.list_blobs_user(prefix, user_id)
blob_storage.download_file_user(blob_name, user_id)

# After (uses main container with session paths)
blob_storage.upload_file_session(content, blob_name, user_id)
blob_storage.list_blobs_session(user_id, prefix=prefix)
blob_storage.download_file_session(blob_name, user_id)
```

## Migration Steps

### Step 1: Stop Using User-Specific Containers

The blob storage service has both methods:
- **Old Methods**: `upload_file_user()`, `download_file_user()`, `list_blobs_user()`
- **New Methods**: `upload_file_session()`, `download_file_session()`, `list_blobs_session()`

✅ **Code has been updated to use session-based methods**

### Step 2: Manual Data Migration (if needed)

If you have existing data in wrong containers, you can migrate it:

```python
from app.services.blob_storage import blob_storage

def migrate_user_data(user_id: str, old_container_suffix: str):
    """Migrate data from user-specific container to session-based structure"""
    
    # Create new session for migrated data
    session_id = blob_storage.create_session(user_id, "Migrated Data")
    
    # List all blobs in old user container
    old_container = f"resumes-{old_container_suffix}"
    
    # Note: You'll need to implement this manually using Azure Storage Explorer
    # or Azure CLI since the current blob service doesn't support cross-container operations
    
    print(f"Please manually move data from container '{old_container}' to main 'resumes' container")
    print(f"Target path: {user_id}/{session_id}/")

# Example usage:
# migrate_user_data("rajiv.ranjan.forasoftware.in", "rajiv-ranjan-forasoftware-in")
```

### Step 3: Clean Up Using Azure Storage Explorer

#### Method 1: Azure Storage Explorer GUI
1. Open Azure Storage Explorer
2. Connect to your storage account
3. Navigate to the blob containers
4. **For Extra Reports Folder**: Delete the standalone `reports/` container if it exists
5. **For User Containers**: 
   - Copy data from `resumes-{user}` containers to main `resumes` container
   - Use path structure: `{user_id}/session_{timestamp}/`
   - Delete empty user containers

#### Method 2: Azure CLI Commands
```bash
# List all containers
az storage container list --account-name resume1raw

# Copy blobs from user container to main container
az storage blob copy start-batch \
  --source-container "resumes-rajiv-ranjan-forasoftware-in" \
  --destination-container "resumes" \
  --destination-path "rajiv.ranjan.forasoftware.in/session_20250117_100000/" \
  --account-name resume1raw

# Delete old user container after verification
az storage container delete \
  --name "resumes-rajiv-ranjan-forasoftware-in" \
  --account-name resume1raw
```

### Step 4: Test New Structure

After migration, test the new structure:

```python
# Test script
from app.services.blob_storage import blob_storage

def test_new_structure():
    user_id = "test@example.com"
    
    # Create session
    session_id = blob_storage.create_session(user_id)
    print(f"Created session: {session_id}")
    
    # Upload test file
    test_content = b"Test resume content"
    url = blob_storage.upload_file_session(test_content, "raw_resumes/test.txt", user_id)
    print(f"Uploaded to: {url}")
    
    # List files
    files = blob_storage.list_blobs_session(user_id, prefix="raw_resumes/")
    print(f"Files in session: {files}")
    
    # Verify structure
    expected_path = f"{user_id}/{session_id}/raw_resumes/test.txt"
    all_blobs = blob_storage.list_blobs(prefix=user_id)
    print(f"All user blobs: {all_blobs}")
    
    return expected_path in [blob for blob in all_blobs]

# Run test
success = test_new_structure()
print(f"Structure test: {'PASSED' if success else 'FAILED'}")
```

## Expected Final Structure

After migration, your blob storage should look like:

```
resumes/ (main container)
├── rajiv.ranjan.forasoftware.in/
│   ├── session_20250117_100000/
│   │   ├── .metadata.json
│   │   ├── raw_resumes/
│   │   │   ├── resume1.pdf
│   │   │   └── resume2.pdf
│   │   ├── processed/
│   │   │   ├── resume1.pdf.txt
│   │   │   └── resume2.pdf.txt
│   │   └── reports/
│   │       └── ranked_resumes.json
│   └── session_20250117_143000/
│       └── raw_resumes/
│           └── resume3.pdf
├── guest/
│   └── session_20250117_120000/
│       └── raw_resumes/
│           └── guest_resume.pdf
└── other_user@email.com/
    └── session_20250117_150000/
        └── raw_resumes/
```

## Verification Steps

1. **Check Container List**: Only `resumes` container should exist (no user-specific ones)
2. **Check Path Structure**: All files should be under `{user_id}/{session_id}/` paths
3. **Test Upload**: Upload a new file and verify it goes to correct session path
4. **Test Download**: Download existing files using session-based methods
5. **Test Listing**: List files using session-based methods

## Rollback Plan

If issues occur, you can temporarily:
1. Keep old methods available (they're still in the code)
2. Restore data from backups if available
3. Use Azure Storage Explorer to manually fix paths

## Benefits After Migration

1. **Proper Organization**: Files organized by user and session
2. **Easy Cleanup**: Can delete entire sessions
3. **Session Tracking**: Know when files were uploaded
4. **Consistent Structure**: All files in one container with logical paths
5. **Future-Proof**: Supports session management features