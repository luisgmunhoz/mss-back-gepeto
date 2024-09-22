import os
import openai
from openai import OpenAI

import json
from dataclasses import dataclass
import sm_utils


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

    medical_data_str = json.dumps(
        {
            "weight": weight,
            "height": height,
            "bmi": bmi,
            "message": message,
            "exams": exams_data,
            "appointments": appointments_data,
            "medications": meds_data,
            "birthday": birthday,
        }
    )
    openai_secret_name = os.environ["OPENAI_SECRET_NAME"]
    openai_secret = sm_utils.get_secret(openai_secret_name)
    client = OpenAI(api_key=openai_secret)
    prompt = f"The following data are, exams, bmi, weight, height, birthday, appointments booked and recurring meds the patient takes, do a analysis based on the users question:\n\n{medical_data_str}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": message,
            },
        ],
        max_tokens=1500,  # Adjust based on the amount of data and response size you expect
        temperature=0.2,  # Lower temperature for more factual responses
    )

    # Get the text output from the response
    analysis = response.choices[0].message.content

    # Print or save the analysis
    print("Analysis:")
    print(analysis)
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "weight": weight,
                "height": height,
                "bmi": bmi,
                "request": message,
                "message": analysis,
                "exams": exams_data,
                "appointments": appointments_data,
                "medications": meds_data,
                "birthday": birthday,
            }
        ),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
