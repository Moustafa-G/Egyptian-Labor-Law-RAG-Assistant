import os

import httpx
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


class APIError(Exception):
    """Raised when the backend can't be reached or returns an error."""
    pass


def ask_question(question: str, timeout: float = 60.0) -> dict:
    """
    Send a question to the backend /query endpoint.
    Returns {"answer": str, "sources": list[str]}.
    Raises APIError with a user-friendly message on failure.
    """
    try:
        response = httpx.post(
            f"{API_BASE_URL}/query",
            json={"question": question},
            timeout=timeout,
        )
    except httpx.ConnectError:
        raise APIError(
            f"Couldn't reach the backend at {API_BASE_URL}. "
            "Is it running? (uvicorn app.main:app --reload)"
        )
    except httpx.TimeoutException:
        raise APIError("The backend took too long to respond. Try again.")

    if response.status_code == 503:
        raise APIError("The backend is still loading the vector store. Wait a moment and try again.")

    if response.status_code == 422:
        raise APIError("Please enter a valid question.")

    if response.status_code != 200:
        raise APIError(f"Backend returned an unexpected error (status {response.status_code}).")

    return response.json()


def check_health() -> dict | None:
    """Returns the /health response, or None if the backend is unreachable."""
    try:
        response = httpx.get(f"{API_BASE_URL}/health", timeout=5.0)
        if response.status_code == 200:
            return response.json()
    except httpx.RequestError:
        pass
    return None