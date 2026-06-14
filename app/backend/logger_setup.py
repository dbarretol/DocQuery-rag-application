import logging
from pythonjsonlogger import json
from app.backend.middleware import request_id_ctx

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        return True

def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.addFilter(RequestIDFilter())
    
    # Ensure handlers are set up correctly
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        # Include request_id in the formatter
        formatter = json.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(request_id)s %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
        
    return logger
