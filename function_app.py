import logging
import azure.functions as func
from blob_trigger.process_pdf import blob_bp

app = func.FunctionApp()
app.register_functions(blob_bp)

logging.info("Successfully registered blueprint blob trigger function!")