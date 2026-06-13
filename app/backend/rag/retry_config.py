import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from google.genai.errors import ServerError, ClientError

logger = logging.getLogger("uvicorn")

# Define common retry strategy for API issues
retry_on_api_errors = retry(
    retry=retry_if_exception_type((ServerError, ClientError)),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(5),
    before_sleep=lambda retry_state: logger.warning(
        f"Retrying Gemini API call after error: {retry_state.outcome.exception()}. "
        f"Attempt {retry_state.attempt_number}..."
    ),
    reraise=True
)
