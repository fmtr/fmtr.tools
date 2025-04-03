from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from fmtr.tools.logging_tools import logger


class Authenticator:
    """

    Authenticate via link or saved token

    """

    PATH = None
    SCOPES = []
    SERVICE = None
    VERSION = None
    PORT = 0

    @classmethod
    def auth(cls):
        msg = f'Doing auth for service {cls.SERVICE} ({cls.VERSION})...'
        logger.info(msg)

        PATH_CREDS = cls.PATH / 'credentials.json'
        PATH_TOKEN = cls.PATH / f'{cls.SERVICE}.json'

        if PATH_TOKEN.exists():
            data_token = PATH_TOKEN.read_json()
            credentials = Credentials.from_authorized_user_info(data_token, cls.SCOPES)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(PATH_CREDS, cls.SCOPES)
            credentials = flow.run_local_server(open_browser=False, port=cls.PORT)
            PATH_TOKEN.write_text(credentials.to_json())
        service = build(cls.SERVICE, cls.VERSION, credentials=credentials)
        return service
