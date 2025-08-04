import boto3


def instantiate_boto3_session(access_key, secret_key, region):
    """
    This function instantiates a boto3 session
    Note: You need to have a .env file in the background
    that has two variables defined
    AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
    """
    my_session = boto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )
    return my_session
