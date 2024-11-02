from datetime import datetime
import os
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import InputSerializer
from openai import OpenAI
from t2.settings import OPEN_AI_KEY


class HealthAssistantView(APIView):
    def post(self, request):
        serializer = InputSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            weight = data.get("weight")
            height = data.get("height")
            bmi = data.get("bmi")
            message = data.get("message")
            birthday = data.get("birthday")
            exams_data = data.get("exams_data", [])
            appointments_data = data.get("appointments_data", [])
            meds_data = data.get("meds_data", [])
            prev_messages = data.get("messages", [])
            gender = data.get("gender", "indefinido")
            age = None
            if birthday:
                age = (
                    (
                        datetime.now() - datetime.fromisoformat(birthday[:-1])
                    ).total_seconds()
                    / 60
                    / 60
                    / 24
                    / 365
                )

            client = OpenAI(api_key=OPEN_AI_KEY)

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
                analysis = self.get_analysis(message, prev_messages, client, prompt)
                return Response(
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
                    },
                    status=status.HTTP_200_OK,
                )

            df = pd.concat((pd.DataFrame(d) for d in exams_data), ignore_index=True)[
                ["Data", "RESULTADOS", "ANALITOS", "VALORES DE REFERÊNCIA"]
            ].dropna(subset=["RESULTADOS"])
            df["Timestamp"] = df["Data"].apply(lambda x: x["seconds"])
            df = df.drop(columns=["Data"])
            data = df.to_dict(orient="records")

            prompt += f" e teve dados de exames: {data}, você deve responder sua pergunta em português."
            analysis = self.get_analysis(message, prev_messages, client, prompt)

            return Response(
                {
                    "message": analysis,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_analysis(self, message, prev_messages, client, prompt):
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
        analysis = response.choices[0].message.content
        return analysis
