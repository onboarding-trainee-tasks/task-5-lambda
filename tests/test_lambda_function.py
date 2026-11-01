
import unittest
from unittest.mock import Mock, patch

import requests

# Avoid creating a real AWS client during unit tests.
with patch("boto3.client"):
    import lambda_function


class TestLambdaFunction(unittest.TestCase):

    def setUp(self):
        self.site = {
            "name": "example",
            "url": "https://example.com",
        }

        self.metric_patcher = patch(
            "lambda_function.cloudwatch.put_metric_data"
        )
        self.mock_metric = self.metric_patcher.start()
        self.addCleanup(self.metric_patcher.stop)

    @patch("lambda_function.requests.get")
    def test_http_200(self, mock_get):
        mock_get.return_value.status_code = 200

        result = lambda_function.lambda_handler(
            {"sites": [self.site]}, None
        )

        self.assertEqual(result["checked_sites"], 1)
        self.assertTrue(result["results"][0]["available"])
        self.assertEqual(result["results"][0]["status_code"], 200)

        self.mock_metric.assert_called_once()
        metric = self.mock_metric.call_args.kwargs["MetricData"][0]
        self.assertEqual(metric["Value"], 1)

    @patch("lambda_function.requests.get")
    def test_http_500(self, mock_get):
        mock_get.return_value.status_code = 500

        result = lambda_function.lambda_handler(
            {"sites": [self.site]}, None
        )

        self.assertFalse(result["results"][0]["available"])
        self.assertEqual(result["results"][0]["status_code"], 500)

        metric = self.mock_metric.call_args.kwargs["MetricData"][0]
        self.assertEqual(metric["Value"], 0)

    @patch("lambda_function.requests.get")
    def test_timeout(self, mock_get):
        mock_get.side_effect = requests.Timeout("Request timed out")

        result = lambda_function.lambda_handler(
            {"sites": [self.site]}, None
        )

        self.assertFalse(result["results"][0]["available"])
        self.assertIsNone(result["results"][0]["status_code"])
        self.assertIn("timed out", result["results"][0]["error"])

        metric = self.mock_metric.call_args.kwargs["MetricData"][0]
        self.assertEqual(metric["Value"], 0)

    def test_missing_sites(self):
        with self.assertRaises(ValueError):
            lambda_function.lambda_handler({}, None)

        self.mock_metric.assert_not_called()

    @patch("lambda_function.requests.get")
    def test_multiple_sites(self, mock_get):
        mock_get.side_effect = [
            Mock(status_code=200),
            Mock(status_code=503),
        ]

        sites = [
            {"name": "first", "url": "https://first.example.com"},
            {"name": "second", "url": "https://second.example.com"},
        ]

        result = lambda_function.lambda_handler(
            {"sites": sites}, None
        )

        self.assertEqual(result["checked_sites"], 2)
        self.assertTrue(result["results"][0]["available"])
        self.assertFalse(result["results"][1]["available"])
        self.assertEqual(self.mock_metric.call_count, 2)


if __name__ == "__main__":
    unittest.main()
