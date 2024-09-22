from datetime import datetime, timedelta
import os
from openai import OpenAI
import pandas as pd

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
    messages: list[dict]
    gender: str
    meds_data: list
    birthday: str


@dataclass
class Output:
    message: str


def lambda_handler(event, context):
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
    prev_messages = body.get("messages", [])
    gender = body.get("gender", "indefinido")

    openai_secret_name = os.environ["OPENAI_SECRET_NAME"]
    open_ai_api_key = sm_utils.get_secret(openai_secret_name)
    client = OpenAI(api_key=open_ai_api_key)

    df = pd.concat((pd.DataFrame(d) for d in exams_data), ignore_index=True)[
        ["Data", "RESULTADOS", "ANALITOS", "VALORES DE REFERÊNCIA"]
    ].dropna(subset=["RESULTADOS"])
    df["Timestamp"] = df["Data"].apply(lambda x : x["seconds"])
    df = df.drop(columns=["Data"])
    sample = df.sample(len(df) // 10)
    data = sample.to_dict(orient="records")
    age = (
        (datetime.now() - datetime.fromisoformat(birthday[:-1])).total_seconds()
        / 60
        / 60
        / 24
        / 365
    )
    prompt = f"o Usuário é do sexo: {gender}, tem imc: {bmi}, peso: {weight} kg, altura: {height}m, idade: {age} e teve dados de exames: {data}, você deve responder sua pergunta em português."

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            *prev_messages,
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": f"Responda em português: {message}",
            },
        ],
        max_tokens=120,  # Adjust based on the amount of data and response size you expect
        temperature=0.4,  # Lower temperature for more factual responses
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
