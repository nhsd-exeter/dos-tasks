import pytest
import os


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["MOTO_ALLOW_NONEXISTENT_REGION"] = 'True'
    os.environ["AWS_DEFAULT_REGION"] = "antarctica"
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_ACCOUNT_ID'] = '123456789012'
