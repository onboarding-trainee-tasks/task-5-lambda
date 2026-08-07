import json
import logging
import os

import boto3
import requests


logger = logging.getLogger()
logger.setLevel(logging.INFO)

cloudwatch = boto3.client("cloudwatch")

METRIC_NAMESPACE = os.getenv(
    "METRIC_NAMESPACE",
    "Task5/WebAvailability",
)

METRIC_NAME = os.getenv(
    "METRIC_NAME",
    "Availability",
)


def lambda_handler(event, context):
    url = event.get("url")
    site_name = event.get("site_name")

    if not url:
        raise ValueError("The event does not contain 'url'")

    if not site_name:
        raise ValueError("The event does not contain 'site_name'")

    status_code = None
    error_message = None
    is_available = False

    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True,
        )

        status_code = response.status_code

        # Any HTTP status from 200 through 299 is successful.
        is_available = 200 <= status_code < 300

        if not is_available:
            error_message = (
                f"Website returned HTTP status {status_code}"
            )

    except requests.RequestException as error:
        # Timeouts, DNS problems, connection errors and TLS errors
        # mean that the website is unavailable.
        is_available = False
        error_message = str(error)

    metric_value = 1 if is_available else 0

    cloudwatch.put_metric_data(
        Namespace=METRIC_NAMESPACE,
        MetricData=[
            {
                "MetricName": METRIC_NAME,
                "Dimensions": [
                    {
                        "Name": "SiteName",
                        "Value": site_name,
                    }
                ],
                "Value": metric_value,
                "Unit": "Count",
            }
        ],
    )

    result = {
        "site_name": site_name,
        "url": url,
        "available": is_available,
        "status_code": status_code,
        "error": error_message,
    }

    logger.info(json.dumps(result))

    return result