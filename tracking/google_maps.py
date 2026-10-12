import logging

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


class GoogleMapsService:
    BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    TIMEOUT = 10

    @classmethod
    def geocode_address(cls, address):
        if not address:
            raise ValueError("Address is required.")

        api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)

        if not api_key:
            raise RuntimeError(
                "GOOGLE_MAPS_API_KEY is not configured."
            )

        try:
            response = requests.get(
                cls.BASE_URL,
                params={
                    "address": address,
                    "key": api_key,
                },
                timeout=cls.TIMEOUT,
            )

            response.raise_for_status()

        except requests.Timeout as exc:
            logger.exception("Google Maps request timed out.")
            raise RuntimeError(
                "Geolocation service timed out."
            ) from exc

        except requests.RequestException as exc:
            logger.exception(
                "Google Maps request failed: %s",
                exc,
            )
            raise RuntimeError(
                "Geolocation service is unavailable."
            ) from exc

        data = response.json()

        if data.get("status") != "OK":
            logger.warning(
                "Google Maps geocoding failed: %s",
                data.get("status"),
            )

            raise ValueError(
                data.get(
                    "error_message",
                    "Address could not be geocoded.",
                )
            )

        result = data["results"][0]

        location = result["geometry"]["location"]

        return {
            "formatted_address": result["formatted_address"],
            "latitude": location["lat"],
            "longitude": location["lng"],
            "place_id": result.get("place_id"),
        }

    @classmethod
    def reverse_geocode(cls, latitude, longitude):
        api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)

        if not api_key:
            raise RuntimeError(
                "GOOGLE_MAPS_API_KEY is not configured."
            )

        try:
            response = requests.get(
                cls.BASE_URL,
                params={
                    "latlng": f"{latitude},{longitude}",
                    "key": api_key,
                },
                timeout=cls.TIMEOUT,
            )

            response.raise_for_status()

        except requests.Timeout as exc:
            logger.exception(
                "Google Maps reverse geocoding timed out."
            )
            raise RuntimeError(
                "Geolocation service timed out."
            ) from exc

        except requests.RequestException as exc:
            logger.exception(
                "Google Maps reverse geocoding failed: %s",
                exc,
            )
            raise RuntimeError(
                "Geolocation service is unavailable."
            ) from exc

        data = response.json()

        if data.get("status") != "OK":
            raise ValueError(
                data.get(
                    "error_message",
                    "Location could not be resolved.",
                )
            )

        result = data["results"][0]

        return {
            "formatted_address": result["formatted_address"],
            "place_id": result.get("place_id"),
        }