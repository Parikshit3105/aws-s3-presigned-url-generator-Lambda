# S3 Presigned URL Generator Lambda Function

## Overview

This AWS Lambda function generates long-lived presigned URLs for S3 objects, with the ability to retrieve credentials securely from AWS Systems Manager Parameter Store.

## Features

- Generate presigned URLs valid for up to 7 days
- Secure credential management using AWS SSM Parameter Store
- Flexible object key selection
- Error handling for various AWS service interactions

## Prerequisites

- AWS Account
- AWS CLI configured
- Python 3.8+
- Boto3 library
- AWS IAM permissions to create Lambda functions, SSM parameters, and S3 access

## Project Structure

```
s3-presigned-url-generator/
│
├── lambda_function.py         # Main Lambda function code
├── requirements.txt            # Python dependencies
├── iam_policy.json             # Lambda IAM policy
└── README.md                  # Project documentation
```

## Setup Instructions

### 1. AWS Systems Manager Parameter Store Setup

1. Navigate to AWS Systems Manager > Parameter Store
2. Create two parameters with the following details:
   - Name: `s3-presigned-credentials-access_key`
     - Type: SecureString
     - Value: Your AWS Access Key
   
   - Name: `s3-presigned-credentials-secret_key`
     - Type: SecureString
     - Value: Your AWS Secret Key

### 2. Lambda Function Configuration

#### Environment Variables

Configure the following environment variables in your Lambda function:

| Variable Name             | Description                               | Example Value          |
|---------------------------|-------------------------------------------|------------------------|
| `BUCKET_NAME`             | S3 Bucket Name                            | `test-delele-me-1234321` |
| `OBJECT_KEY`              | Default S3 Object Key                     | `index.html`           |
| `AWS_ACCESS_KEY_PARAM`    | SSM Parameter for Access Key              | `s3-presigned-credentials-access_key` |
| `AWS_SECRET_KEY_PARAM`    | SSM Parameter for Secret Key              | `s3-presigned-credentials-secret_key` |
| `PRESIGNED_URL_EXPIRATION`| URL Expiration in Seconds (7 days = 604800)| `604800`               |

### 3. IAM Permissions

1. Create a new IAM role for the Lambda function
2. Attach the IAM policy provided in `iam_policy.json`
3. Ensure the policy allows:
   - SSM Parameter retrieval
   - S3 presigned URL generation
   - CloudWatch Logs creation

### 4. Lambda Function Deployment

#### Local Development
1. Clone the repository
2. Create a virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

#### AWS Deployment
1. Zip the function code
2. Upload via AWS Lambda console or AWS CLI
3. Configure the environment variables
4. Set the handler to `lambda_function.lambda_handler`

## Usage

### Invoking the Lambda

The function can be triggered with an optional `object_key` in the event payload:

```json
{
  "object_key": "custom/path/file.txt"
}
```

If no `object_key` is provided, it uses the default from environment variables.

### Response Format

Successful invocation returns:
```json
{
  "statusCode": 200,
  "body": {
    "presigned_url": "https://your-s3-url",
    "expiration_time": "2024-01-01 12:00:00 UTC"
  }
}
```

## Security Considerations

- Rotate SSM parameter credentials regularly
- Limit IAM role permissions to minimum required
- Use least privilege principles

## Troubleshooting

- Check CloudWatch logs for detailed error messages
- Verify SSM parameter names and values
- Confirm S3 bucket and object key exist

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

[Specify your license here]

## Contact

[Your contact information or support channel]
