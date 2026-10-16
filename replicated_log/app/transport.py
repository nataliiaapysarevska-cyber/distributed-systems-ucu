import httpx
import logging
import os

logger = logging.getLogger(__name__)
TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "15"))
class HttpTransport:

    def send(self, master, secondary_url, message, sequence):
        response = httpx.post(
            f"{secondary_url}/replicate",
            json={"message": message, "sequence": sequence},
            timeout=TIMEOUT
        )

        response.raise_for_status()
        logger.info("ACK received from %s for message %s, seq_N=%s", secondary_url, message, sequence)

        return True