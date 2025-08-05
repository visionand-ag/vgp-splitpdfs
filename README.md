# PDF Splitter - Azure Function

A serverless Azure Function that automatically processes PDF documents by detecting divider pages and splitting them into separate documents. The split PDFs are then uploaded to SharePoint for organized document management.

## 🚀 Overview

This Azure Function monitors a blob storage container for uploaded PDF files and automatically:
1. **Detects divider pages** using text extraction or OCR (Optical Character Recognition)
2. **Splits PDFs** into separate documents based on divider locations
3. **Uploads split documents** to SharePoint with timestamped filenames
4. **Moves processed files** to a "processed" container for archival

## 🏗️ Architecture

```
PDF Upload → Blob Storage → Azure Function → PDF Processing → SharePoint Upload
                ↓
         Processed Container (Archive)
```

### Key Components

- **Blob Trigger**: Monitors `pdfs/` container for new PDF uploads
- **PDF Processing**: Hybrid approach using text extraction + OCR fallback
- **SharePoint Integration**: Certificate-based authentication for document upload
- **Error Handling**: Comprehensive logging and exception management

## 📋 Features

### ✨ Smart Divider Detection
- **Fast Path**: Text-based divider detection for searchable PDFs
- **Fallback Path**: OCR-based detection for image-based or scanned PDFs
- **Parallel Processing**: Multi-threaded OCR for improved performance

### 🔒 Secure SharePoint Integration
- Certificate-based authentication with Azure AD
- Automatic file uploads with timestamp-based naming
- Connection testing and error recovery

### 📊 Comprehensive Logging
- Detailed execution tracking
- Error reporting with stack traces
- Performance monitoring

### 🐳 Container Ready
- Docker support for consistent deployments
- Multi-language OCR support (German, English, French, Italian)
- Optimized for Azure Functions runtime

## ✅ Deployment Checklist

Before running the deployment scripts, ensure you have:

- [ ] Azure CLI installed and authenticated (`az login`)
- [ ] Docker installed (for containerized deployment)
- [ ] Proper Azure subscription permissions (Contributor role minimum)
- [ ] Unique resource names configured in `deploy.sh`
- [ ] Certificate files generated and placed in `certs/` directory
- [ ] `settings.json` file created with all required environment variables
- [ ] SharePoint site and document library accessible
- [ ] Azure AD app registration permissions configured

### Quick Start Commands

```bash
# 1. Clone and navigate to project
git clone <repository-url>
cd vgp-splitpdfs

# 2. Configure deployment variables
nano deploy.sh  # Edit resource names and location

# 3. Run infrastructure deployment
chmod +x deploy.sh && ./deploy.sh

# 4. Create settings.json with your environment variables
nano settings.json

# 5. Apply application settings
chmod +x app_settings.sh && ./app_settings.sh

# 6. Upload certificate to Azure AD app registration (manual step)
# 7. Test with a sample PDF upload
```

## 🛠️ Setup & Installation

### Prerequisites

- Azure Subscription with:
  - Azure Functions App
  - Azure Storage Account (2 containers: `pdfs`, `processed-pdfs`)
  - Application registration with certificate authentication
- SharePoint site with document library access
- Docker (for containerized deployment)

### 1. Environment Configuration

Create a `.env` file or configure Application Settings:

```env
# Azure AD Configuration
TENANT_NAME=your-tenant.onmicrosoft.com
TENANT_ID=your-tenant-id
CLIENT_ID=your-app-registration-id
CLIENT_SECRET=your-client-secret

# SharePoint Configuration
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite
SHAREPOINT_SITE_NAME=YourSiteName
SHAREPOINT_DOC_LIBRARY=/sites/yoursite/Shared Documents

# Storage Account Configuration
SA_URL=https://yourstorageaccount.blob.core.windows.net
SA_NAME=yourstorageaccount
SA_CONTAINER_NAME_PDFS=pdfs
SA_CONTAINER_NAME_PROCESSED_PDFS=processed-pdfs
SA_CONN_STR=DefaultEndpointsProtocol=https;AccountName=...

# Certificate Configuration
CERTIFICATE_PATH=certs/split-pdfs.pem
THUMBPRINT=your-certificate-thumbprint

# Processing Configuration
DIVIDER_TEXT=DIVIDER_PAGE_TEXT
```

### 2. Certificate Setup

1. Generate a certificate for Azure AD app registration:
```bash
openssl req -x509 -newkey rsa:2048 -keyout split-pdfs.key -out split-pdfs.cer -days 365 -nodes
openssl pkcs12 -export -out split-pdfs.pfx -inkey split-pdfs.key -in split-pdfs.cer
openssl x509 -inform DER -in split-pdfs.cer -out split-pdfs.pem
```

2. Upload the `.cer` file to your Azure AD app registration
3. Place certificate files in the `certs/` directory

### 3. Automated Deployment with Scripts
