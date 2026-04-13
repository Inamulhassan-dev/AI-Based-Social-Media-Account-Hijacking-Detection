import logging

import requests

logger = logging.getLogger(__name__)


def get_geolocation(ip_address):
    try:
        if ip_address in ["127.0.0.1", "localhost", "::1"]:
            return {
                "country": "Local",
                "city": "Localhost",
                "latitude": 0.0,
                "longitude": 0.0,
                "timezone": "UTC",
                "isp": "Local",
                "is_vpn": False,
            }

        response = requests.get(
            f"http://ip-api.com/json/{ip_address}?fields=status,message,country,city,lat,lon,timezone,isp,proxy",
            timeout=5,
        )
        data = response.json()

        if data.get("status") == "success":
            return {
                "country": data.get("country", "Unknown"),
                "city": data.get("city", "Unknown"),
                "latitude": data.get("lat", 0.0),
                "longitude": data.get("lon", 0.0),
                "timezone": data.get("timezone", "UTC"),
                "isp": data.get("isp", "Unknown"),
                "is_vpn": data.get("proxy", False),
            }
    except Exception as exc:
        logger.error("Geolocation error: %s", exc)

    return {
        "country": "Unknown",
        "city": "Unknown",
        "latitude": 0.0,
        "longitude": 0.0,
        "timezone": "UTC",
        "isp": "Unknown",
        "is_vpn": False,
    }
