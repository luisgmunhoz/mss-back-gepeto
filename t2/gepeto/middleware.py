import os
from django.http import JsonResponse
from firebase_admin import auth, initialize_app
from t2.settings import FIREBASE_SECRET_PATH


class FirebaseAppSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            FIREBASE_SECRET = FIREBASE_SECRET_PATH
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = FIREBASE_SECRET
            cls._instance = initialize_app()
        return cls._instance


class FirebaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        FirebaseAppSingleton.get_instance()

    def __call__(self, request):
        # authorization = request.headers.get("Authorization", "")
        # if authorization == "":
        #     authorization = request.headers.get("authorization", "")
        # authorization_token = authorization.split(" ")
        # if len(authorization_token) != 2:
        #     return JsonResponse({"detail": "Invalid token"}, status=403)
        # token = authorization_token[1]

        # try:
        #     decoded_token = auth.verify_id_token(token)
        #     request.uid = decoded_token["uid"]
        # except Exception:
        #     return JsonResponse({"detail": "Invalid token"}, status=403)

        response = self.get_response(request)
        return response
