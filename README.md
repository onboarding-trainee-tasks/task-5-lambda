# Onboarding Task 5 - Website Availability Checker (Lambda)

This repository contains a Python AWS Lambda function that checks website availability and publishes custom metrics to Amazon CloudWatch. Infrastructure and deployment are managed in the `task-5-infra` repository.

## Implementation Features

- Checks multiple websites supplied in the invocation event
- Treats HTTP 2xx responses as available; reports HTTP errors and request timeouts as unavailable
- Publishes `Task5/WebAvailability` / `Availability` metrics (1 = available, 0 = unavailable), with a `SiteName` dimension
- Logs structured JSON results to CloudWatch Logs
- Packages the function and the `requests` dependency as separate ZIP files (Lambda Layer)
- Uses GitHub Actions to build packages and trigger the infrastructure deployment workflow after a push to `main`

## Requirements

- Python 3 and `pip`
- Bash and `zip`
- Internet access to install dependencies during packaging
- The `task-5-infra` repository for AWS deployment

## Build

```bash
git clone https://github.com/onboarding-trainee-tasks/task-5-lambda.git
cd task-5-lambda

bash build.sh
```

Generated files:

```text
dist/lambda-function.zip
dist/requests-layer.zip
```

The `dist/` directory is excluded from Git. Rebuild packages before a manual Terraform plan/apply in the infrastructure repository.

## Lambda event

```json
{
  "sites": [
    {"name": "google", "url": "https://google.com"},
    {"name": "github", "url": "https://github.com"}
  ]
}
```

The function returns the number of checked sites and an individual result for each site. CloudWatch metric publishing and scheduled invocation are configured in the infrastructure repository.

## GitHub Actions

Pull requests to `main` and pushes to `main` build the ZIP packages and upload them as workflow artifacts. On pushes to `main`, a separate job dispatches the Terraform workflow in `task-5-infra`, passing the Lambda commit SHA.

Required GitHub configuration:

- Repository variable: `INFRA_REPOSITORY` (e.g., `onboarding-trainee-tasks/task-5-infra`)
- Repository secret: `INFRA_WORKFLOW_TOKEN` (token with permission to dispatch the infrastructure workflow)

The dispatch job confirms the request was sent; review the subsequent `task-5-infra` run to confirm deployment.
