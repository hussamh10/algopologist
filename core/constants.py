import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if 'H:' in BASE_DIR:
    LAB = 301
else:
    LAB = 317

if LAB == 301:
    print('LAB 301...')

    BASE_DIR = "H:\\Desktop\\algopologist"
    DATA_DIR = "H:\\Desktop\\algopologist\\data"
    C_DATA_DIR = "C:\\Users\\hbb\\Desktop"

    # SESSIONS_PATH = os.path.join(BASE_DIR, 'data', 'sessions')
    SESSIONS_PATH = os.path.join(C_DATA_DIR, 'sessions')

    CONTINUE_GOOGLE_X = 1800
    CONTINUE_GOOGLE_Y = 234
    GOT_IT_X = 1140
    GOT_IT_Y = 726
    CHROME_VERSION = 124



if LAB == 317:  # Windows
    print('LAB 317...')
    CONTINUE_GOOGLE_X = 2300
    CONTINUE_GOOGLE_Y = 233
    GOT_IT_X = 1140
    GOT_IT_Y = 726

    if os.name == 'posix':        
        BASE_DIR = '/Users/hussam/Desktop/Projects/algopologist'
        DATA_DIR = '/Users/hussam/Desktop/Projects/algopologist/data'
        CHROME_VERSION = 124

    else:
        BASE_DIR = "C:\\Users\\hussa\\Desktop\\algopologist"
        DATA_DIR = "C:\\Users\\hussa\\Desktop\\algopologist\\data"
        CHROME_VERSION = 124
    
    SESSIONS_PATH = os.path.join(BASE_DIR, 'data', 'sessions')


print(f'BASE_DIR: {BASE_DIR}')

# Click positions
CHROME_REMIND_X = 950
CHROME_REMIND_Y = 185
WAIT_TIME = 10
SMALL_WAIT_TIME = 1

# Set the paths using os.path.join for OS compatibility
LOGGING_PATH = os.path.join(BASE_DIR, 'data', 'logging')
SCREENSHOTS_PATH = os.path.join(BASE_DIR, 'data', 'screenshots')
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


_PRAW_PATH = os.path.join(BASE_DIR, 'res', 'praw.json')
try:
    PRAW = json.load(open(_PRAW_PATH))
except:
    print("praw file not found")
    

MIN_MEMBERS = 5000

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
