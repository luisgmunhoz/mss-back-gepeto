import json
from dataclasses import dataclass
import os
from typing import Optional
from firebase_admin import credentials, initialize_app, firestore, App
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


@dataclass
class Output:
    message: str


def lambda_handler(event, context):
    FirebaseAppSingleton.get_instance()
    print(event)
    uid = event.get("requestContext", {}).get("authorizer", {}).get("uid")
    print("uid: ", uid)
    client = firestore.client()
    initial_path = "users/" + uid
    doc_ref = client.document(initial_path)
    doc = doc_ref.get()
    if not doc.exists:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "User not found"}),
            "headers": {"Access-Control-Allow-Origin": "*"},
        }
    user_data = doc.to_dict()
    weight = user_data.get("weight")
    print("weight: ", weight)
    height = user_data.get("height")
    print("height: ", height)
    bmi = None
    if weight is not None and height is not None:
        bmi = weight / (height**2)
    print("bmi: ", bmi)
    exams_col = doc_ref.collection("exams")
    exams = exams_col.stream()
    exams_data = [exam.to_dict() for exam in exams]
    appointments_col = doc_ref.collection("appointments")
    appointments = appointments_col.stream()
    appointments_data = [appointment.to_dict() for appointment in appointments]
    meds_col = doc_ref.collection("medications")
    meds = meds_col.stream()
    meds_data = [med.to_dict() for med in meds]
    birthday = user_data.get("birthday").isoformat()
    message = event.get("body")

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
