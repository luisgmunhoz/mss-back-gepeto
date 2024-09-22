from infra.services import Services


class GepetoConfig:
    def __init__(self, services: Services) -> None:
        function = services.aws_lambda.create_function(
            name="Gepeto",
            path="./functions/gepeto",
            description="Uma função lambda que manda os exames e a mensagem do chat do usuário para o ChatGPT analisar",  # noqa: E501
            layers=[
                services.layers.openai_layer,
                services.layers.sm_utils_layer,
            ],
            environment={
                "OPENAI_SECRET_NAME": services.secrets_manager.openai_secret.secret_name
            },
        )
        services.secrets_manager.openai_secret.grant_read(function)

        services.api_gateway.create_endpoint("POST", "/gepeto", function)
