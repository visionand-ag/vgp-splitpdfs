FROM mcr.microsoft.com/azure-functions/python:4-python3.9

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-ita \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

# Copy requirements first for better caching
COPY requirements.txt /home/site/wwwroot/
RUN pip install --no-cache-dir -r /home/site/wwwroot/requirements.txt

# Copy the rest of the application
COPY . /home/site/wwwroot

# Set working directory
WORKDIR /home/site/wwwroot

# Ensure proper permissions
RUN chmod -R 755 /home/site/wwwroot