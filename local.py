import os
from unittest.mock import MagicMock

import lambda_function

os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"


lambda_function.cloudwatch.put_metric_data = MagicMock()


event = {
    "url": "https://google.com",
    "site_name": "Google",
}


class Context:
    aws_request_id = "local-test-request"


result = lambda_function.lambda_handler(
    event,
    Context(),
)

print(result)