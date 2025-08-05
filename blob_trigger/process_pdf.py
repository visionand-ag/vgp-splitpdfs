import os
import sys
import logging
import tempfile
import concurrent.futures
from io import BytesIO
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../..")

# Azure and PDF Processing Libraries
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from PyPDF2 import PdfWriter, PdfReader
from pdf2image import convert_from_path
import pytesseract

# Shared Project Modules
from shared.config.env_config import get_config
from shared.o365_sharepoint.upload_sp import upload_pdf_sp
from office365.sharepoint.client_context import ClientContext

# --- Load Configuration ---
config = get_config()

# --- Blueprint for Azure Function ---
blob_bp = func.Blueprint()


# =============================================================================
# 1. CORE LOGIC - DIVIDER DETECTION
# =============================================================================

def find_dividers_by_text(inputpdf: PdfReader, divider_text: str) -> list:
    """
    Rapidly identifies divider pages by extracting existing text (Fast Path).
    Returns a list of page numbers that are dividers.
    """
    logging.info("Attempting to find dividers using fast text extraction...")
    divider_pages = []
    for page_num, page in enumerate(inputpdf.pages):
        try:
            if divider_text.lower() in page.extract_text().lower():
                logging.info(f"Text-based divider found on page {page_num + 1}.")
                divider_pages.append(page_num)
        except Exception as e:
            logging.warning(f"Could not extract text from page {page_num + 1}. It might be an image. Error: {e}")
            continue
    return divider_pages

def ocr_page_for_divider(args):
    """
    Helper function for parallel OCR. Performs OCR on one page.
    Returns the page index if the divider is found, otherwise None.
    """
    page_index, page_image, divider_text = args
    try:
        logging.info(f"Performing OCR on page {page_index + 1}...")
        # Using a simplified language set for robustness. Add more if needed.
        text = pytesseract.image_to_string(page_image, lang='deu+eng')
        if divider_text.lower() in text.lower():
            logging.info(f"OCR-based divider found on page {page_index + 1}.")
            return page_index
    except Exception as e:
        logging.error(f"Error during OCR on page {page_index + 1}: {e}")
    return None

def find_dividers_by_ocr(pdf_path: str, divider_text: str) -> list:
    """
    Converts PDF to images and finds dividers using parallelized OCR (Fallback Path).
    """
    logging.info("Falling back to OCR-based divider detection.")
    try:
        images = convert_from_path(pdf_path, 300)
        logging.info(f"Converted {len(images)} pages to images for OCR.")

        divider_pages = []
        tasks = [(i, images[i], divider_text) for i in range(len(images))]

        # Use ThreadPoolExecutor for parallel I/O-bound (image conversion) and CPU-bound (OCR) tasks
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(ocr_page_for_divider, tasks)
            for result in results:
                if result is not None:
                    divider_pages.append(result)
        
        return sorted(divider_pages)

    except Exception as e:
        logging.error(f"An error occurred during the OCR process: {e}")
        # This could be a Poppler or Tesseract issue.
        raise


# =============================================================================
# 2. UTILITY FUNCTIONS (Splitting, Uploading, Moving)
# =============================================================================

def create_page_groups(total_pages: int, divider_pages: list) -> list:
    """
    Creates groups of page numbers to be split into separate documents.
    The divider pages themselves are excluded from the output.
    """
    if not divider_pages:
        logging.info("No dividers found. Treating entire PDF as a single document.")
        return [list(range(total_pages))]

    page_groups = []
    start_page = 0
    for divider_page in sorted(divider_pages):
        # Add the group of pages before the divider
        group = list(range(start_page, divider_page))
        if group:
            page_groups.append(group)
        # The next group starts after the divider page
        start_page = divider_page + 1
    
    # Add the final group of pages after the last divider
    final_group = list(range(start_page, total_pages))
    if final_group:
        page_groups.append(final_group)
        
    logging.info(f"Created {len(page_groups)} page groups from {total_pages} pages.")
    return page_groups

def _upload_to_sharepoint(pdf_buffer: BytesIO, output_filename: str, blob_name: str):
    """Uploads a PDF from a memory buffer to SharePoint."""
    cert_credentials = {
        "tenant": config['tenant_id'],
        "client_id": config['client_id'],
        "thumbprint": "A7DB32FDD4B4BCE2FB332740449B01B942E9F97C",
        "cert_path": "certs/split-pdfs.pem"
    }
    
    logging.info(f"Attempting to upload {output_filename} to SharePoint...")
    try:
        ctx = ClientContext(config['sharepoint_site_url']).with_client_certificate(**cert_credentials)
        logging.info("ClientContext created successfully for SharePoint upload.")
        upload_pdf_sp(pdf_buffer, ctx, output_filename)
        logging.info(f"Successfully uploaded {output_filename} to SharePoint for original blob: {blob_name}")
    except Exception as e:
        logging.error(f"SharePoint upload for PDF {output_filename} failed: {e}")
        raise

def create_and_upload_pdfs(inputpdf: PdfReader, page_groups: list, base_filename: str, blob_name: str):
    """
    Creates new PDF files in memory from page groups and uploads them to SharePoint.
    """
    output_filenames = []
    for i, group in enumerate(page_groups):
        if not group:
            continue

        output = PdfWriter()
        for page_num in group:
            output.add_page(inputpdf.pages[page_num])

        # Create a unique filename
        timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
        output_filename = f"{base_filename}_doc_{i+1}_{timestamp}.pdf"

        try:
            pdf_buffer = BytesIO()
            output.write(pdf_buffer)
            pdf_buffer.seek(0)
            logging.info(f"Created PDF in memory: {output_filename}")

            # --- SharePoint Upload ---
            _upload_to_sharepoint(pdf_buffer, output_filename, blob_name)
            output_filenames.append(output_filename)

        except Exception as e:
            logging.error(f"Failed to create or upload PDF for group {i+1} ('{output_filename}'): {e}")
            continue
            
    return output_filenames

def move_blob_to_processed(blob_name: str):
    """Moves the original blob to the processed container."""
    try:
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=config['sa_url'], credential=credential)
        
        source_container_name = config['sa_container_name_pdfs']
        target_container_name = config['sa_container_name_processed_pdfs']

        # Ensure blob_name doesn't have the container prefix
        if blob_name.startswith(f"{source_container_name}/"):
            blob_name = blob_name[len(f"{source_container_name}/"):]

        source_blob_client = blob_service_client.get_blob_client(source_container_name, blob_name)
        target_blob_client = blob_service_client.get_blob_client(target_container_name, blob_name)

        logging.info(f"Moving '{blob_name}' to container '{target_container_name}'...")
        target_blob_client.start_copy_from_url(source_blob_client.url)
        source_blob_client.delete_blob()
        logging.info(f"Successfully moved '{blob_name}'.")

    except Exception as e:
        logging.error(f"Error moving blob '{blob_name}': {e}")
        raise


# =============================================================================
# 3. AZURE FUNCTION TRIGGER
# =============================================================================

@blob_bp.function_name("SplitPDF")
@blob_bp.blob_trigger(arg_name="pdfblob", path="pdfs/{name}", connection="AzureWebJobsStorage")
def blob_trigger(pdfblob: func.InputStream):
    logging.info(f"Processing PDF blob: {pdfblob.name}")
    
    # Use a temporary file to handle the PDF data
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(pdfblob.read())
        temp_file_path = temp_file.name

    try:
        inputpdf = PdfReader(temp_file_path)
        total_pages = len(inputpdf.pages)
        base_filename = os.path.splitext(os.path.basename(pdfblob.name))[0]
        divider_text = config['divider_text']

        # --- HYBRID LOGIC ---
        # 1. Try the fast text-based method first
        divider_pages = find_dividers_by_text(inputpdf, divider_text)

        # 2. If no dividers are found, fall back to the slower OCR method
        if not divider_pages:
            logging.info("No text-based dividers found. Attempting OCR fallback.")
            divider_pages = find_dividers_by_ocr(temp_file_path, divider_text)
        
        # 3. Create page groups based on the findings
        page_groups = create_page_groups(total_pages, divider_pages)
        
        # 4. Process the groups and upload the resulting PDFs
        if page_groups:
            create_and_upload_pdfs(inputpdf, page_groups, base_filename, pdfblob.name)
        else:
            logging.warning("No pages to process after grouping.")

        # 5. Move the original blob to the processed container on success
        move_blob_to_processed(pdfblob.name)
        logging.info(f"Successfully completed processing for {pdfblob.name}")

    except Exception as e:
        logging.error(f"An unhandled error occurred during processing of {pdfblob.name}: {e}", exc_info=True)
        # Depending on requirements, you might move the blob to an 'error' container here
        raise

    finally:
        # Ensure the temporary file is always cleaned up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            logging.info(f"Cleaned up temporary file: {temp_file_path}")