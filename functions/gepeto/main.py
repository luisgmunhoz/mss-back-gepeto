import json
from dataclasses import dataclass
import os
from typing import Optional
from firebase_admin import credentials, initialize_app, App
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


@dataclass
class Input:
    message: str
    weight: float
    height: float
    bmi: float
    exams_data: list
    appointments_data: list
    meds_data: list
    birthday: str


@dataclass
class Output:
    message: str


def lambda_handler(event, context):
    FirebaseAppSingleton.get_instance()
    print(event)
    uid = event.get("requestContext", {}).get("authorizer", {}).get("uid")
    print("uid: ", uid)
    body = json.loads(event["body"])
    weight = body.get("weight")
    height = body.get("height")
    bmi = body.get("bmi")
    message = body.get("message")
    birthday = body.get("birthday")
    exams_data = body.get("exams", [])
    appointments_data = body.get("appointments", [])
    meds_data = body.get("medications", [])

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "weight": weight,
                "height": height,
                "bmi": bmi,
                "request": message,
                "message": "Hello from Gepeto!",
                "exams": exams_data,
                "appointments": appointments_data,
                "medications": meds_data,
                "birthday": birthday,
            }
        ),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
