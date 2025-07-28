import boto3
import json
from botocore.awsrequest import AWSRequest
from botocore.auth import SigV4Auth
import requests


def subscribe(principal_id, principal_type="USER"):
    """Make a request to AmazonQDeveloperService.CreateAssignment"""

    # Get AWS credentials
    session = boto3.Session()
    credentials = session.get_credentials()

    # Prepare payload
    payload = {"principalId": principal_id, "principalType": principal_type}

    # Create request
    request = AWSRequest(
        method="POST",
        url="https://codewhisperer.us-east-1.amazonaws.com/",
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/x-amz-json-1.0",
            "X-Amz-Target": "AmazonQDeveloperService.CreateAssignment",
            "X-Amz-User-Agent": "aws-sdk-js/2.1594.0 promise",
        },
    )

    # Sign with service name 'q'
    SigV4Auth(credentials, "q", "us-east-1").add_auth(request)

    # Send request
    response = requests.post(
        request.url, headers=dict(request.headers), data=request.body
    )

    return response
