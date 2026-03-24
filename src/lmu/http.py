import json
import logging
import time
from http import client as http_lib
from threading import Lock
from typing import Optional

MAX_RETRIES = 3
RETRY_DELAY = 0.1  # seconds


class HTTPSession:
    """Simple HTTP session class for connection pooling using http.client.

    Thread-safe implementation with retry logic and proper connection lifecycle management.
    """

    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._connection: Optional[http_lib.HTTPConnection] = None
        self._lock = Lock()

    def _get_connection(self) -> http_lib.HTTPConnection:
        """Get or create a persistent HTTP connection (thread-safe)."""
        with self._lock:
            if self._connection is None:
                self._connection = http_lib.HTTPConnection(self.host, self.port, timeout=self.timeout)
            return self._connection

    def _reset_connection(self) -> None:
        """Reset the connection (thread-safe)."""
        with self._lock:
            if self._connection:
                try:
                    self._connection.close()
                except Exception:
                    pass
            self._connection = None

    def request(self, method: str, url: str, data: Optional[bytes] = None,
                headers: Optional[dict] = None, retry_count: int = 0) -> 'HTTPResponse':
        """Send an HTTP request using the persistent connection with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            url: Request URL path
            data: Optional request body data
            headers: Optional request headers
            retry_count: Current retry attempt number

        Returns:
            HTTPResponse object with status, text, and headers

        Raises:
            Exception: If all retry attempts fail
        """
        try:
            conn = self._get_connection()
            with self._lock:
                req_headers = headers or {}
                if data:
                    req_headers['Content-Type'] = 'application/json'
                    req_headers['Content-Length'] = str(len(data))
                conn.request(method, url, body=data, headers=req_headers)
                response = conn.getresponse()
                return HTTPResponse(response.status, response.read().decode('utf-8'), response.getheaders())
        except (http_lib.HTTPException, ConnectionError, OSError, TimeoutError) as e:
            # Connection might be stale, recreate it and retry
            self._reset_connection()

            if retry_count < MAX_RETRIES:
                logging.warning(
                    "HTTP request failed (attempt %d/%d) to %s %s: %s. Retrying...",
                    retry_count + 1, MAX_RETRIES, method, url, type(e).__name__
                )
                time.sleep(RETRY_DELAY * (retry_count + 1))  # Exponential backoff
                return self.request(method, url, data, headers, retry_count + 1)

            logging.error(
                "HTTP request failed after %d attempts: %s %s://%s:%s%s - %s: %s",
                MAX_RETRIES, method, "http", self.host, self.port, url, type(e).__name__, e
            )
            raise
        except Exception as e:
            logging.error(
                "Unexpected error during HTTP request: %s %s://%s:%s%s - %s: %s",
                method, "http", self.host, self.port, url, type(e).__name__, e
            )
            raise

    def get(self, url: str, timeout: Optional[float] = None) -> 'HTTPResponse':
        """Send a GET request."""
        if timeout:
            self.timeout = timeout
        return self.request('GET', url)

    def post(self, url: str, data: Optional[bytes] = None,
             json_data: Optional[dict] = None, headers: Optional[dict] = None) -> 'HTTPResponse':
        """Send a POST request."""
        body = json.dumps(json_data).encode('utf-8') if json_data else data
        return self.request('POST', url, data=body, headers=headers)

    def put(self, url: str, data: Optional[bytes] = None,
            json_data: Optional[dict] = None, headers: Optional[dict] = None) -> 'HTTPResponse':
        """Send a PUT request."""
        body = json.dumps(json_data).encode('utf-8') if json_data else data
        return self.request('PUT', url, data=body, headers=headers)

    def close(self) -> None:
        """Close the persistent connection and release resources."""
        self._reset_connection()


class HTTPResponse:
    """Simple HTTP response wrapper."""

    def __init__(self, status_code: int, text: str, headers: list):
        self.status_code = status_code
        self.text = text
        self.headers = dict(headers)
        self._json = None

    def json(self):
        if self._json is None:
            self._json = json.loads(self.text)
        return self._json
