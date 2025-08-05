from office365.sharepoint.client_context import ClientContext
import os, sys
from dotenv import load_dotenv, find_dotenv
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../..")
from shared.config.env_config import get_config
import logging

load_dotenv(find_dotenv())
config = get_config()

# test site connection
def test_sharepoint_connection(ctx: ClientContext):
    try:
        # Get the SharePoint web information
        web = ctx.web.get().execute_query()
        logging.info("Connection successful!")
        logging.info(f"Connected to SharePoint site: {web.url}")
        logging.info(f"Site title: {web.title}")
        
    except Exception as e:
        logging.info(f"Connection failed with error: {e}")
        return False

def upload_pdf_sp(file_content, ctx, file_name=None):
    try:
        _ = test_sharepoint_connection(ctx)
        logging.info(f"Attempting to connect to Library: {config['sharepoint_doc_library']}")
        target_url = f"{config['sharepoint_doc_library']}"
        target_folder = ctx.web.get_folder_by_server_relative_url(target_url)
        logging.info(f"Server relative URL: {target_url}")
        
        # Handle both file paths and BytesIO objects
        if isinstance(file_content, str):
            try:
                file_name = os.path.basename(file_content)
                logging.info(f"Uploading PDF: {file_content}")
                with open(file_content, "rb") as file_data:
                    target_folder.upload_file(
                        file_name=file_name,
                        content=file_data
                    ).execute_query()
            except FileNotFoundError:
                logging.error(f"File not found: {file_content}")
                raise
            except IOError as e:
                logging.error(f"Error reading file {file_content}: {e}")
                raise
        else:
            try:
                logging.info(f"Uploading PDF from memory: {file_name}")
                target_folder.upload_file(
                    file_name=file_name,
                    content=file_content
                ).execute_query()
            except Exception as e:
                logging.error(f"Error uploading file from memory: {e}")
                raise
            
        logging.info("PDF uploaded successfully!")
        
    except Exception as e:
        logging.error(f"Failed to upload PDF: {e}")
        raise