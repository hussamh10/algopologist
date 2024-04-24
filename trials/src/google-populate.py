import os.path
import sys
import json

sys.path.append(os.path.join('Users', 'hussam', 'Desktop', 'Projects', 'algopologist')) # 317 win
sys.path.append('../../')
sys.path.append(os.path.join('H:/', 'Desktop', 'algopologist')) # 301 lab
sys.path.append(os.path.join('C:/', 'Users', 'hussa', 'Desktop', 'algopologist')) # 317 win

import core.constants as constants
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import names

from core.constants import IP_DB_NAME, BASE_DIR

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/admin.directory.user"]

def signin():
  """Shows basic usage of the Admin SDK Directory API.
  Prints the emails and names of the first 10 users in the domain.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  token_path = os.path.join(constants.KEY_DIR, 'token.json')
  creds_path = os.path.join(constants.KEY_DIR, 'admin-credentials.json')
  if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token_path, "w") as token:
      token.write(creds.to_json())

  service = build("admin", "directory_v1", credentials=creds)
  return service

def getUsers(service):
    print("Getting the first 10 users in the domain")
    results = (
      service.users()
      .list(customer="my_customer", maxResults=10, orderBy="email")
      .execute()
  )
    users = results.get("users", [])

    if not users:
      print("No users in the domain.")
    else:
      print("Users:")
      for user in users:
        print(f"{user['primaryEmail']} ({user['name']['fullName']})")


def addUser(service, user):
    print("Creating a new user")
    results = service.users().insert(body=user).execute()
    print(f"User created: {results['primaryEmail']}")

def getEmails(xp):
    emails = []
    config_path = os.path.join(BASE_DIR, 'trials', 'data', xp, 'config.json')
    config = json.load(open(config_path, 'r'))
    users = config['users']
    for user in users:
        emails.append(users[user]['email'])
    return emails

if __name__ == "__main__":
  experiment = sys.argv[1]
  service = signin()
  getUsers(service)
  emails = getEmails(experiment)
  print(emails)
  for email in emails:
      try:
        user = {
          "name": {
            "familyName": names.get_last_name(),
            "givenName": names.get_first_name(),
          },
          "password": constants.BASIC_PASSWORD,
          "primaryEmail": email,
        }
        addUser(service, user)
      except Exception as e:
         pass