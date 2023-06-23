import time
from typing import NamedTuple

import requests

MAX_WAIT_TIME = 60
WAIT_MULTIPLIER = 2
BASE_WAIT_TIME = 1


class PhoneNumber(NamedTuple):
    request_id: int
    number: str


def get_temp_phone_number(token: str, country_id: int) -> PhoneNumber:
    """
    Get a temporary phone number from SMS Man.

    Args:
        token: The token that will be used to send the request.
        country_id: The country id of the country that the phone number will be from.

    Returns:
        A PhoneNumber object containing the request id and the phone number.
    """

    SMS_MAN_GET_NUMBER_BASE_URL = "http://api.sms-man.com/control/get-number"
    MICROSOFT_APP_ID = 133

    wait_time = BASE_WAIT_TIME
    while True:
        res = requests.get(
            f"{SMS_MAN_GET_NUMBER_BASE_URL}?token={token}&country_id={country_id}&application_id={MICROSOFT_APP_ID}"
        )

        # Check for errors
        if not res.status_code == 200:
            raise requests.RequestException(f"Error while getting temporary phone number: {res.status_code}")
        elif "error_code" in res.json() and res.json()["error_code"] == "no_numbers":
            # Wait for a bit and try again (no numbers available)
            print(f"[SMS-MAN] No numbers available... Retry in {wait_time} seconds")
            time.sleep(wait_time)
            wait_time *= WAIT_MULTIPLIER
            if wait_time >= MAX_WAIT_TIME:
                raise requests.RequestException(
                    f"Waited for too long! Error while getting temporary phone number: {res.json()['error_msg']}"
                )
            continue
        elif "error_msg" in res.json():
            raise requests.RequestException(f"Error while getting temporary phone number: {res.json()['error_msg']}")

        print("[SMS-MAN] Temporary phone number acquired!")
        return PhoneNumber(request_id=res.json()["request_id"], number=res.json()["number"])


def get_sms_code(token: str, phone_number: PhoneNumber) -> str:
    """
    Get the SMS code from a temporary phone number.

    Args:
        token: The token that will be used to send the request.
        phone_number: The phone number to get the SMS code from.

    Returns:
        The SMS code.
    """

    SMS_MAN_GET_SMS_BASE_URL = "http://api.sms-man.com/control/get-sms"

    wait_time = BASE_WAIT_TIME
    while True:
        res = requests.get(f"{SMS_MAN_GET_SMS_BASE_URL}?token={token}&request_id={phone_number.request_id}")

        # Check for errors
        if not res.status_code == 200:
            raise requests.RequestException(f"Error while getting SMS code: {res.status_code}")
        elif "error_code" in res.json() and res.json()["error_code"] == "wait_sms":
            # Wait for a bit and try again (no sms yet)
            print(f"[SMS-MAN] Waiting for SMS... Retry in {wait_time} seconds")
            time.sleep(wait_time)
            wait_time *= WAIT_MULTIPLIER
            if wait_time >= MAX_WAIT_TIME:
                raise requests.RequestException(
                    f"Waited for too long! Error while getting SMS code: {res.json()['error_msg']}"
                )
            continue
        elif "error_msg" in res.json():
            raise requests.RequestException(f"Error while getting SMS code: {res.json()['error_msg']}")

        print("[SMS-MAN] SMS code acquired!")
        return res.json()["sms_code"]
