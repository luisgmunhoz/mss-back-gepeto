from datetime import datetime
import os
from openai import OpenAI
import pandas as pd

import json
from dataclasses import dataclass
import sm_utils
from typing import Any, Dict, Literal, List, TypedDict


@dataclass
class Input:
    message: str
    weight: float
    height: float
    bmi: float
    exams_data: List[Dict[str, Any]]
    appointments_data: List[Dict[str, Any]]
    messages: List[Dict[str, str]]
    gender: str
    meds_data: List
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
    exams_data = body.get("exams_data", [])
    appointments_data = body.get("appointments_data", [])
    meds_data = body.get("meds_data", [])
    prev_messages = body.get("messages", [])
    gender = body.get("gender", "indefinido")
    age = None
    if birthday:
        age = (
            (datetime.now() - datetime.fromisoformat(birthday[:-1])).total_seconds()
            / 60
            / 60
            / 24
            / 365
        )

    openai_secret_name = os.environ["OPENAI_SECRET_NAME"]
    open_ai_api_key = sm_utils.get_secret(openai_secret_name)
    client = OpenAI(api_key=open_ai_api_key)

    # Constructing the prompt
    prompt = f"Você é um assistente de saúde e só sabe sobre saúde ajude como puder mas apenas questões de saúde, se apresente como Dr. Flamingo, o assistente virtual da YE, foque em dar dicas médicas, não faça textos longos. Seu Usuário é do sexo: {gender}, tem imc: {bmi}, peso: {weight} kg, altura: {height}m, idade: {age}"

    if appointments_data:
        prompt += f" e tem as seguintes consultas marcadas: {', '.join([a['description'] for a in appointments_data])} "
    else:
        prompt += " e não tem consultas marcadas. "

    if meds_data:
        prompt += f" e tem as seguintes medicações cadastradas: {', '.join([m['name'] for m in meds_data])} "
    else:
        prompt += " e não tem medicações cadastradas. "

    if not exams_data:
        prompt += " e não tem dados de exames cadastrados, você deve responder sua pergunta em português e recomendar que ele cadastre seus exames no sistema."
        analysis = get_analysis(message, prev_messages, client, prompt)
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

    df = pd.concat((pd.DataFrame(d) for d in exams_data), ignore_index=True)[
        ["Data", "RESULTADOS", "ANALITOS", "VALORES DE REFERÊNCIA"]
    ].dropna(subset=["RESULTADOS"])
    df["Timestamp"] = df["Data"].apply(lambda x: x["seconds"])
    df = df.drop(columns=["Data"])
    data = df.to_dict(orient="records")

    prompt += f" e teve dados de exames: {data}, você deve responder sua pergunta em português."
    analysis = get_analysis(message, prev_messages, client, prompt)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": analysis,
            }
        ),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }


def get_analysis(
    message: str, prev_messages: List[Dict[str, str]], client: OpenAI, prompt: str
) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            *prev_messages,
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": message,
            },
        ],
        max_tokens=360,
        temperature=0.4,
    )
    # Get the text output from the response
    analysis = response.choices[0].message.content
    return analysis
