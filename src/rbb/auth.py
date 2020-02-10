import praw
import sys

def reddit_from_program_args():
    if len(sys.argv) != 6:
        print("Please provide: <client_id> <client_secret> <user_agent> <username> <password>")
        sys.exit(1)
    _, client_id, client_secret, user_agent, username, password = sys.argv

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        username=username,
        password=password)
