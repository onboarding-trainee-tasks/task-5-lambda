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


def publish_metric(site_name, is_available):
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


def check_site(site):
    site_name = site.get("name")
    url = site.get("url")

    if not site_name:
        raise ValueError("Site does not contain 'name'")

    if not url:
        raise ValueError(
            f"Site '{site_name}' does not contain 'url'"
        )

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

        if 200 <= status_code < 300:
            is_available = True
        else:
            error_message = (
                f"Website returned HTTP status {status_code}"
            )

    except requests.RequestException as error:
        error_message = str(error)

    publish_metric(
        site_name,
        is_available,
    )

    result = {
        "name": site_name,
        "url": url,
        "available": is_available,
        "status_code": status_code,
        "error": error_message,
    }

    logger.info(json.dumps(result))

    return result


def lambda_handler(event, context):
    sites = event.get("sites")

    if not sites:
        raise ValueError(
            "The event does not contain a 'sites' array"
        )

    results = []

    for site in sites:
        result = check_site(site)
        results.append(result)

    return {
        "checked_sites": len(results),
        "results": results,
    }