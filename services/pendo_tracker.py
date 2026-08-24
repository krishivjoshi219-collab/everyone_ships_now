import time
import logging
import requests

logger = logging.getLogger(__name__)

PENDO_TRACK_URL = "https://data.pendo.io/data/track"
PENDO_INTEGRATION_KEY = "c505ec8b-651a-46b2-89d7-1a6bc74e9fe4"


def track(event_name: str, visitor_id: str = "system", account_id: str = "system", properties: dict = None):
    try:
        payload = {
            "type": "track",
            "event": event_name,
            "visitorId": visitor_id,
            "accountId": account_id,
            "timestamp": int(time.time() * 1000),
            "properties": properties or {}
        }
        requests.post(
            PENDO_TRACK_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "x-pendo-integration-key": PENDO_INTEGRATION_KEY
            },
            timeout=(3, 5)
        )
    except Exception:
        logger.debug(f"Pendo track event '{event_name}' failed to send")
