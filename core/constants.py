import os
import json


LAB = 301

# Determine the base directory based on the operating system
if LAB == 301:
    print('LAB 301...')

    BASE_DIR = "H:\\Desktop\\algopologist"
    DATA_DIR = "H:\\Desktop\\algopologist\\data"
    
    CONTINUE_GOOGLE_X = 1800
    CONTINUE_GOOGLE_Y = 234

if LAB == 317:  # Windows
    CONTINUE_GOOGLE_X = 2300
    CONTINUE_GOOGLE_Y = 233

    if os.name == 'posix':        
        BASE_DIR = '/Users/hussam/Desktop/Projects/Platform behavior'
        DATA_DIR = '/Users/hussam/Desktop/Projects/Platforms behavior/data'

    else: # Unix-like systems (Linux, macOS)
        BASE_DIR = "C:\\Users\\hussa\\Desktop\\algopologist"
        DATA_DIR = "C:\\Users\\hussa\\Desktop\\algopologist\\data"


# Set the paths using os.path.join for OS compatibility
LOGGING_PATH = os.path.join(BASE_DIR, 'data', 'logging')
SCREENSHOTS_PATH = os.path.join(BASE_DIR, 'data', 'screenshots')
SESSIONS_PATH = os.path.join(BASE_DIR, 'data', 'sessions')
USERS_PATH = os.path.join(BASE_DIR, 'data', 'users')
DATABASE = os.path.join(BASE_DIR, 'data', 'signals.db')

IP_DB_NAME = os.path.join(BASE_DIR, 'data', 'ip.db')
IP_FILE = os.path.join(BASE_DIR, 'res', 'data', 'ip.txt')
TAKEN_IP_FILE = os.path.join(BASE_DIR, 'res', 'data', 'taken.txt')
CURRENT_IP_FILE = os.path.join(BASE_DIR, 'res', 'data', 'current-ip.txt')

SERVER_PORT = 61234

KEY_DIR = os.path.join(BASE_DIR, 'res')

_EMAIL = os.path.join(BASE_DIR, 'res', 'email.json')
try:
    EMAIL = json.load(open(_EMAIL))
except:
    print("Email file not found")
    EMAIL = {'email': '', 'password': ''}


_PASS_PATH = os.path.join(BASE_DIR, 'res', 'passwords.json')
try:
    passwords = json.load(open(_PASS_PATH))
    BASIC_PASSWORD = passwords['basic']
    COMPLEX_PASSWORD = passwords['complex']
except:
    print("Password file not found")
    BASIC_PASSWORD = 'password'
    COMPLEX_PASSWORD = 'password'

def getPlatform(platform_name):
    platform_name = platform_name.lower()
    if platform_name == 'reddit':
        from core.platforms.Reddit import Reddit
        return Reddit
    elif platform_name == 'facebook':
        from core.platforms.Facebook import Facebook
        return Facebook
    elif platform_name == 'instagram':
        from core.platforms.Instagram import Instagram
        return Instagram
    elif platform_name == 'twitter':
        from core.platforms.Twitter import Twitter
        return Twitter
    elif platform_name == 'youtube':
        from core.platforms.Youtube import Youtube
        return Youtube
    elif platform_name == 'tiktok':
        from core.platforms.TikTok import TikTok
        return TikTok
    else:
        raise Exception('Platform not supported')