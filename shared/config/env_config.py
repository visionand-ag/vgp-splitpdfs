from dotenv import load_dotenv
import os

def get_config():
    """
    Load environment variables from .env file.
    """
    load_dotenv()
    return {
        "tenant_name": os.getenv("TENANT_NAME"),
        "tenant_id": os.getenv("TENANT_ID"),
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "sharepoint_site_url" : os.getenv("SHAREPOINT_SITE_URL"),
        "sharepoint_site_name" : os.getenv("SHAREPOINT_SITE_NAME"),
        "sharepoint_doc_library" : os.getenv("SHAREPOINT_DOC_LIBRARY"),
        "sa_url": os.getenv("SA_URL"),
        "sa_name": os.getenv("SA_NAME"),
        "sa_container_name_pdfs": os.getenv("SA_CONTAINER_NAME_PDFS"),
        "sa_container_name_processed_pdfs": os.getenv("SA_CONTAINER_NAME_PROCESSED_PDFS"),
        "sa_conn_str": os.getenv("SA_CONN_STR"),
        "certificate_path": os.getenv("CERTIFICATE_PATH"),
        "thumbprint": os.getenv("THUMBPRINT"),
        "divider_text": os.getenv("DIVIDER_TEXT"),
    }
