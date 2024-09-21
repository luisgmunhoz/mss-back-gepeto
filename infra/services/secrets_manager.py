from aws_cdk import aws_secretsmanager as sm


class SecretsManager:
    def __init__(self, scope, context) -> None:
        self.svc_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="SvcSecret",
            secret_complete_arn="arn:aws:secretsmanager:sa-east-1:396608797965:secret:prod/app/firebase_svc_acc_key-cJFoqg",
        )
