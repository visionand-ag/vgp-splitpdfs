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

### 3. Deployment Options

#### Option A: Docker Deployment
```bash
# Build the container
docker build -t vgp-splitpdfs .

# Deploy to Azure Container Registry
az acr build --registry myregistry --image vgp-splitpdfs .
```

#### Option B: Direct Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Deploy using Azure Functions Core Tools
func azure functionapp publish your-function-app-name
```

## 📁 Project Structure

```
vgp-splitpdfs/
├── function_app.py              # Main Azure Function app entry point
├── host.json                    # Function app configuration
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container configuration
├── deploy.sh                    # Deployment script
├── app_settings.sh             # Environment setup script
├── blob_trigger/
│   └── process_pdf.py          # Core PDF processing logic
├── shared/
│   ├── config/
│   │   └── env_config.py       # Environment configuration
│   └── o365_sharepoint/
│       └── upload_sp.py        # SharePoint upload utilities
└── certs/                      # Certificate files
    ├── split-pdfs.cer
    ├── split-pdfs.pem
    └── split-pdfs.pfx
```

## 🔧 Configuration

### Divider Text Configuration
Set the `DIVIDER_TEXT` environment variable to specify what text identifies divider pages:
```env
DIVIDER_TEXT="--- DIVIDER ---"
```

### OCR Language Support
The Docker container includes support for:
- German (`deu`)
- English (`eng`) 
- French (`fra`)
- Italian (`ita`)

Add additional languages by modifying the Dockerfile:
```dockerfile
RUN apt-get install -y tesseract-ocr-spa  # Spanish support
```

## 🚀 Usage

1. **Upload PDF**: Place PDF files in the `pdfs/` blob container
2. **Automatic Processing**: Function triggers automatically on blob upload
3. **Monitor Logs**: Check Azure Function logs for processing status
4. **Retrieve Results**: Split PDFs appear in SharePoint document library
5. **Archive**: Original PDFs move to `processed-pdfs/` container

### Example Output Filenames
```
original-document_doc_1_05082025_143022.pdf
original-document_doc_2_05082025_143022.pdf
original-document_doc_3_05082025_143022.pdf
```

## 📊 Monitoring & Troubleshooting

### Log Analysis
Monitor Function execution through:
- Azure Portal → Function App → Functions → Monitor
- Application Insights (if configured)
- Live Log Stream

### Common Issues

**SharePoint Upload Failures**
- Verify certificate thumbprint matches
- Check SharePoint permissions
- Validate site URL and library path

**Memory Issues with Large PDFs**
- Implement streaming for large files
- Add memory monitoring
- Consider chunked processing

## 🔒 Security Considerations

- **Certificate Security**: Store certificates securely in Azure Key Vault
- **Access Control**: Use managed identities where possible
- **Network Security**: Consider VNet integration for enhanced security
- **Data Privacy**: Ensure compliance with data protection regulations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 About Vision&

Developed by [VisionAnd AG](https://visionand.ch) - Empowering businesses through intelligent document automation solutions.

---

**Last Updated**: August 2025  
**Version**: 1.0.0