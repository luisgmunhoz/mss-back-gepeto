from infra.services import Services


class FirebaseAuthorizerConfig:
    def __init__(self, services: Services) -> None:
        function = services.aws_lambda.create_function(
            name="FirebaseAuthorizer",
            path="./authorizers/firebase_authorizer",
            description="An authorizer to validate requests based on a Bearer token present on the Authorization header",  # noqa: E501
            layers=[services.layers.firebase_admin_layer],
        )

        services.api_gateway.create_authorizer(
            function, name="firebase_authorizer", default=True
        )
