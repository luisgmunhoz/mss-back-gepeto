import os
from typing import Literal, Optional
from firebase_admin import auth, credentials, initialize_app, App
import sm_utils


class FirebaseAppSingleton:
    _instance: Optional[App] = None

    @classmethod
    def get_instance(cls) -> App:
        if cls._instance is None:
            # Retrieve the secret from Secrets Manager
            FIREBASE_SECRET_NAME = os.environ.get("FIREBASE_SECRET_NAME")
            FIREBASE_SECRET = sm_utils.get_secret(FIREBASE_SECRET_NAME)

            cred = credentials.Certificate(FIREBASE_SECRET)
            cls._instance = initialize_app(cred)
        return cls._instance


def lambda_handler(event, context):
    FirebaseAppSingleton.get_instance()
    authorization = event["headers"].get("Authorization", "")
    print("splitting token")
    authorization_token = authorization.split("Bearer ")
    if len(authorization_token) < 2:
        policy = generate_policy("deny")
        print("invalid token")
        return policy
    token = authorization_token[-1]
    print("verifying token")

    try:
        decoded_token = auth.verify_id_token(token)
    except Exception:
        return generate_policy("deny")
    print("token verified")
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
