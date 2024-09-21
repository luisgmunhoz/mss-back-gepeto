import json
import os
from typing import Literal, Optional
from firebase_admin import auth, credentials, initialize_app
import logging

import sm_utils


def lambda_handler(event, context):
    authorization = event["headers"].get("Authorization", "")
    logging.info("splitting token")
    authorization_token = authorization.split("Bearer ")
    if len(authorization_token) < 2:
        policy = generate_policy("deny")
        logging.info("invalid token")
        return policy
    token = authorization_token[-1]
    logging.info("verifying token")
    # Retrieve the secret from Secrets Manager
    FIREBASE_SECRET_NAME = os.environ.get("FIREBASE_SECRET_NAME")
    FIREBASE_SECRET = sm_utils.get_secret(FIREBASE_SECRET_NAME)

    cred = credentials.Certificate(FIREBASE_SECRET)

    initialize_app(cred)

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
