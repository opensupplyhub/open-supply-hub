import os
import logging
from distutils.util import strtobool

import boto3
from botocore.exceptions import ProfileNotFound
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from django.conf import settings

log = logging.getLogger(__name__)


class OpenSearchServiceConnection:
    '''
    The singleton class configures the connection between
    Django and OpenSearch. It exposes a `client` property
    for communicating with the OpenSearch cluster.
    '''

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenSearchServiceConnection, cls) \
                .__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        auth = None
        if not getattr(settings, 'DEBUG', False):
            # Set up AWS authentication only if the application is running in
            # the AWS cloud.
            auth = self.__get_aws_auth()

        host = os.getenv('OPENSEARCH_HOST')
        port = os.getenv('OPENSEARCH_PORT')
        use_ssl = bool(strtobool(
            os.getenv('OPENSEARCH_SSL', 'False')
        ))
        verify_certs = bool(strtobool(
            os.getenv('OPENSEARCH_SSL_CERT_VERIFICATION', 'False')
        ))
        self.__client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=auth,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            connection_class=RequestsHttpConnection
        )

    @property
    def client(self) -> OpenSearch:
        return self.__client

    @staticmethod
    def __get_aws_auth() -> AWSV4SignerAuth:
        try:
            # While running in the AWS environment, the auto-generated AWS
            # credentials for the IAM role assigned to the instance are used.
            credentials = boto3.Session().get_credentials()
        except ProfileNotFound:
            log.error(('[OpenSearch Connection] AWS creds were not found for '
                       'the connection with the OpenSearch cluster.'))
            raise

        region = os.getenv('AWS_DEFAULT_REGION')
        try:
            aws_auth = AWSV4SignerAuth(credentials, region)
        except ValueError:
            log.error(('[OpenSearch Connection] The credentials and AWS '
                       'region values are empty.'))
            raise

        return aws_auth
