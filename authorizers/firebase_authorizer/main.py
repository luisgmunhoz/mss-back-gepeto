from typing import Literal, Optional
from firebase_admin import auth, credentials, initialize_app

cred = credentials.Certificate("./serviceAccountKey.json")
initialize_app(cred)


def lambda_handler(event, context):
    authorization = event["headers"].get("Authorization", "")
    authorization_token = authorization.split("Bearer ")
    if len(authorization_token) < 2:
        policy = generate_policy("deny")
        return policy
    token = authorization_token[-1]
    try:
        decoded_token = auth.verify_id_token(token)
    except Exception:
        return generate_policy("deny")

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
