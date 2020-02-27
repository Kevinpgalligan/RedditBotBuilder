import praw
import sys

class AuthArgs:
    def __init__(self, client_id, client_secret, user_agent, username, password):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.username = username
        self.password = password

class ProgramArgsAuthorisationProvider:
    def get_reddit(self):
        return praw.Reddit(**self._get_program_args().__dict__)

    def get_username(self):
        return self._get_program_args().username

    def _get_program_args(self):
        if len(sys.argv) != 6:
            raise RuntimeError(
                "Couldn't get Reddit credentials from program args. Please provide: <client_id> <client_secret> <user_agent> <username> <password>")
        return AuthArgs(*sys.argv[1:])

class AuthorisationMethod:
    PROGRAM_ARGS = "ProgramArgs"
    CONFIG_FILE = "ConfigFile" # TODO implement this

def get_auth_provider(auth_method):
    if auth_method == AuthorisationMethod.PROGRAM_ARGS:
        return ProgramArgsAuthorisationProvider()
    raise ValueError("Unknown authorisation method '{}'.".format(auth_method))
