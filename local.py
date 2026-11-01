
import os
from unittest.mock import MagicMock

os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"

import lambda_function


lambda_function.cloudwatch.put_metric_data = MagicMock()

event = {
    "sites": [
        {
            "name": "google",
            "url": "https://google.com",
        }
    ]
}

result = lambda_function.lambda_handler(event, None)

print(result)
print(
    "CloudWatch metric calls:",
    lambda_function.cloudwatch.put_metric_data.call_count,
)
