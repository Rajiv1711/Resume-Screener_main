# Azure Blob Storage Integration for Resume Screener

## Overview
The Resume Screener Project has been updated to store all resume files in Azure Blob Storage instead of the local file system. This provides better scalability, reliability, and cloud-native architecture.

## Changes Made

### 1. Configuration Updates
- **File**: `app/config.py`
- **Changes**: Added `BLOB_CONTAINER_NAME = "resumes"` configuration
- **Purpose**: Defines the Azure Blob Storage container name for storing resumes

### 2. New Blob Storage Service
- **File**: `app/services/blob_storage.py`
- **Purpose**: Centralized service for all Azure Blob Storage operations
- **Features**:
  - Upload files to blob storage
  - Download files from blob storage
  - List blobs with prefix filtering
  - Delete blobs
  - Check blob existence
  - Get blob URLs

### 3. Updated Upload Endpoint
- **File**: `app/routers/resumes.py`
- **Changes**:
  - Files are now uploaded directly to Azure Blob Storage
  - Temporary files are created for parsing (since parser expects file paths)
  - Response includes blob URL and blob name
  - Temporary files are cleaned up after parsing

### 4. Enhanced Parser Service
- **File**: `app/services/parser.py`
- **New Functions**:
  - `extract_text_from_blob()`: Extract text from blobs in memory
  - `parse_resume_from_blob()`: Parse resumes directly from blob storage
  - `parse_zip_from_blob()`: Handle ZIP files from blob storage
- **Features**:
  - Processed text is saved to blob storage under `processed/` prefix
  - Maintains backward compatibility with local file processing

### 5. Updated Ranking Service
- **File**: `app/routers/ranking.py`
- **Changes**:
  - Reads resumes from blob storage instead of local directory
  - Uses `blob_storage.list_blobs(prefix="raw_resumes/")` to find all resumes
  - Saves ranked results to both local files and blob storage
  - Error handling for individual resume processing failures

### 6. Enhanced Reporting Service
- **File**: `app/services/report.py`
- **New Function**: `generate_reports_from_blob()`
- **Features**:
  - Reads ranked results from blob storage
  - Generates Excel and PDF reports
  - Uploads reports to blob storage
  - Fallback to local files if blob storage fails

### 7. Updated Reporting Router
- **File**: `app/routers/reporting.py`
- **Changes**:
  - Uses blob storage for report generation
  - New endpoint: `/api/blob-url/{report_type}` to get direct blob URLs
  - Maintains local file download functionality

## Blob Storage Structure

```
resumes/ (container)
├── raw_resumes/
│   ├── resume1.pdf
│   ├── resume2.docx
│   ├── resume3.txt
│   └── batch_resumes.zip
├── processed/
│   ├── resume1.pdf.txt
│   ├── resume2.docx.txt
│   └── resume3.txt.txt
└── reports/
    ├── ranked_resumes.json
    ├── ranked_resumes.xlsx
    └── ranked_resumes.pdf
```

## API Endpoints

### Upload Resume
- **Endpoint**: `POST /api/upload`
- **Response**: Now includes `blob_url` and `blob_name` fields
- **Storage**: Files stored in `raw_resumes/` prefix

### Rank Resumes
- **Endpoint**: `POST /api/rank`
- **Source**: Reads from blob storage `raw_resumes/` prefix
- **Output**: Saves results to both local and blob storage

### Download Reports
- **Endpoint**: `GET /api/download/{report_type}`
- **Types**: `excel` or `pdf`
- **Source**: Generates from blob storage data

### Get Blob URL
- **Endpoint**: `GET /api/blob-url/{report_type}`
- **Purpose**: Get direct blob storage URLs for reports
- **Response**: `{"blob_url": "...", "blob_name": "..."}`

## Benefits of Azure Blob Storage Integration

### 1. Scalability
- No local storage limitations
- Automatic scaling with Azure infrastructure
- Support for large file uploads

### 2. Reliability
- Built-in redundancy and backup
- High availability (99.9% SLA)
- Data durability guarantees

### 3. Security
- Azure AD integration
- Encryption at rest and in transit
- Access control and permissions

### 4. Cost Efficiency
- Pay only for storage used
- No need for local disk management
- Automatic tiering options

### 5. Cloud-Native Architecture
- Better integration with other Azure services
- Easier deployment and scaling
- Centralized data management

## Migration Notes

### Backward Compatibility
- Local file processing still supported
- Gradual migration possible
- Fallback mechanisms in place

### Data Migration
- Existing local files can be uploaded to blob storage
- No data loss during transition
- Both local and blob storage can coexist

### Performance Considerations
- Blob storage operations are asynchronous
- Temporary files used for parsing compatibility
- Caching strategies can be implemented

## Configuration Requirements

### Azure Blob Storage Setup
1. Create Azure Storage Account
2. Create container named "resumes"
3. Update connection string in `app/config.py`
4. Ensure proper access permissions

### Environment Variables
```bash
# Azure Blob Storage
BLOB_CONNECTION_STRING="your-connection-string"
BLOB_CONTAINER_NAME="resumes"
```

### Dependencies
- `azure-storage-blob==12.22.0` (already in requirements.txt)
- Azure Storage Account with appropriate permissions

## Error Handling

### Blob Storage Errors
- Connection failures fall back to local processing
- Individual file errors don't stop batch processing
- Comprehensive error logging and reporting

### File Processing Errors
- Temporary file cleanup on errors
- Graceful degradation for unsupported formats
- Detailed error messages for debugging

## Future Enhancements

### Potential Improvements
1. **Direct Blob Processing**: Eliminate temporary files entirely
2. **Async Processing**: Implement background job processing
3. **Caching**: Add Redis cache for frequently accessed data
4. **Monitoring**: Add Azure Application Insights integration
5. **CDN**: Use Azure CDN for faster file access

### Performance Optimizations
1. **Batch Operations**: Process multiple files in parallel
2. **Streaming**: Stream large files instead of loading into memory
3. **Compression**: Compress files before storage
4. **Indexing**: Add search capabilities for stored resumes

## Testing

### Test Scenarios
1. Upload single resume file
2. Upload ZIP file with multiple resumes
3. Rank resumes from blob storage
4. Generate and download reports
5. Error handling for invalid files
6. Blob storage connectivity issues

### Validation
- Verify files are stored in correct blob locations
- Confirm parsing works with blob-stored files
- Test ranking accuracy with blob storage
- Validate report generation and download

## Monitoring and Maintenance

### Key Metrics
- Blob storage usage and costs
- Upload/download performance
- Error rates and types
- Processing times

### Maintenance Tasks
- Regular cleanup of temporary files
- Monitor blob storage quotas
- Review and optimize storage costs
- Update connection strings and credentials

This integration provides a robust, scalable foundation for the Resume Screener application while maintaining backward compatibility and providing a smooth migration path.
