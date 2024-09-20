import json
from typing import Literal, Optional
from firebase_admin import auth, credentials, initialize_app
import boto3
from botocore.exceptions import ClientError
import logging


def get_secret():
    secret_name = "prod/app/firebase_svc_acc_key"
    region_name = "sa-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    return json.loads(get_secret_value_response["SecretString"])


cred = credentials.Certificate(get_secret())


initialize_app(cred)


def lambda_handler(event, context):
    token = event["headers"].get("secret", "")
    logging.info("verifying token")
    try:
        decoded_token = auth.verify_id_token(token)
    except Exception:
        return generate_policy("deny")
    logging.info("token verified")
    uid = decoded_token["uid"]

    return generate_policy("allow", uid)


def generate_policy(
    effect: Literal["allow", "deny"], uid: Optional[str] = None
) -> dict:
    policy = {
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {"Action": "execute-api:Invoke", "Effect": effect, "Resource": "*"}
            ],
        },
    }
    if effect == "allow" and uid is not None:
        policy["context"] = {"uid": uid}
    return policy
