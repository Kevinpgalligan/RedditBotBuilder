import praw
import sys

class AuthArgs:
    def __init__(self, client_id, client_secret, user_agent, username, password):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.username = username
        self.password = password

def get_program_auth_args():
    if len(sys.argv) != 6:
        print("Please provide: <client_id> <client_secret> <user_agent> <username> <password>")
        sys.exit(1)
    return AuthArgs(*sys.argv[1:])

def get_reddit_username_from_program_args():
    return get_program_auth_args().username

def get_reddit_from_program_args():
    return praw.Reddit(**get_program_auth_args().__dict__)
