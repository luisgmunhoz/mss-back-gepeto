import json
from dataclasses import dataclass


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
