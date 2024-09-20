from aws_cdk import aws_lambda as _lambda
from lambda_forge.path import Path


class Layers:
    def __init__(self, scope) -> None:
        self.firebase_admin_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="FirebaseAdminLayer",
            layer_version_arn="arn:aws:lambda:sa-east-1:396608797965:layer:firebase_admin:1",
        )
