from functions.gepeto.config import GepetoConfig
from authorizers.firebase_authorizer.config import FirebaseAuthorizerConfig
from docs.config import DocsConfig
from aws_cdk import Stack
from constructs import Construct
from infra.services import Services


class LambdaStack(Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:
        super().__init__(scope, f"{context.name}-Lambda-Stack", **kwargs)

        self.services = Services(self, context)

        # Authorizers
        FirebaseAuthorizerConfig(self.services)

        # Docs
        DocsConfig(self.services)

        # Gepeto
        GepetoConfig(self.services)
