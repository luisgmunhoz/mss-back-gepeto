from infra.services import Services


class GepetoConfig:
    def __init__(self, services: Services) -> None:
        function = services.aws_lambda.create_function(
            name="Gepeto",
            path="./functions/gepeto",
            description="Uma função lambda que manda os exames e a mensagem do chat do usuário para o ChatGPT analisar",  # noqa: E501
            layers=[],
        )

        services.api_gateway.create_endpoint("POST", "/gepeto", function)
