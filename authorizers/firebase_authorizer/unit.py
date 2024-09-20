from .main import lambda_handler


def test_authorizer_should_fail_with_invalid_secret():
    event = {"headers": {"Authorization": "Bearer INVALID-SECRET"}}
    response = lambda_handler(event, None)

    assert response == {
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "deny",
                    "Resource": event["methodArn"],
                }
            ],
        },
    }
