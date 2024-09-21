from infra.services import Services


class FirebaseAuthorizerConfig:
    def __init__(self, services: Services) -> None:
        function = services.aws_lambda.create_function(
            name="FirebaseAuthorizer",
            path="./authorizers/firebase_authorizer",
            description="An authorizer to validate requests based on a Bearer token present on the Authorization header",  # noqa: E501
            layers=[
                services.layers.firebase_admin_layer,
                services.layers.sm_utils_layer,
            ],
            environment={
                "FIREBASE_SECRET_NAME": services.secrets_manager.svc_secret.secret_name
            },
        )

        services.secrets_manager.svc_secret.grant_read(function)

        services.api_gateway.create_authorizer(
            function, name="firebase_authorizer", default=True
        )
