import random

from core.account_creation.JuicySMS import juicy
from core.utils.util import convertStringToNumber, wait
from core.platforms.Platform import Platform
from core.utils.log import *
import core.utils.monkey as monkey
import core.constants as constants

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from time import sleep
from datetime import datetime
import names
import os
import imaplib
import sqlite3
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import datetime


# Look into the tab trick

def getMail():
    IMAP_SERVER = 'outlook.office365.com'
    IMAP_PORT = 993
    EMAIL_ACCOUNT = constants.EMAIL['email']
    PASSWORD = constants.EMAIL['password']

    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ACCOUNT, PASSWORD)
    mail.select('inbox')  # Select the inbox

    debug("Getting email code...")
    wait(10)

    codes = []
    status, messages = mail.search(None, 'ALL')
    if status == 'OK':
        messages = messages[0].split()
        for num in messages[-5:]:
            typ, data = mail.fetch(num, '(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    # Parse the email content
                    msg = email.message_from_bytes(response_part[1])
                    # Decode the email subject
                    subject, encoding = decode_header(msg['Subject'])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or 'utf-8')
                    subject = subject.split(' ')

                    email_date = parsedate_to_datetime(msg['Date'])
                    current_time = datetime.datetime.now(datetime.timezone.utc)

                    delta = current_time - email_date
                    if delta < datetime.timedelta(minutes=5):
                        for word in subject:
                            if 'FB-' in word:
                                word = word.split('-')[1]
                                codes.append(word)
    else:
        error('Failed to retrieve emails.')

    # Log out
    mail.logout()
    
    if len(codes) == 0:
        error('No code found')
        return -1

    code = codes[-1]
    debug(f'Email code: {code}')
    return code


class Facebook(Platform):
    name = 'facebook'
    url='https://www.facebook.com'
    search_url='https://www.facebook.com/search/pages/?q=%s'
    creation_url='https://www.facebook.com/reg'
    login_url='https://www.facebook.com/login'

    def __init__(self, userId):
        super().__init__(Facebook.name, Facebook.url, userId)

    def signIn(self):
        self.loadPage(Facebook.login_url)
        wait(2)
        phone = self.getPhone()
        monkey.type(self.getPhone())
        monkey.next()
        monkey.type(constants.BASIC_PASSWORD)
        monkey.enter()

    def createUserMobile(self, info):
        if self.userExists():
            return

        areas = {'USA': '+1', 'NL': '+31' , 'UK': '+44'}
        sms = juicy()

        self.loadPage(Facebook.creation_url)
        sleep(3)
        monkey.click()
        monkey.next()
        monkey.type(info["firstname"])
        monkey.next()
        monkey.type(info["lastname"])
        monkey.next()
        area, phone = sms.get_number('facebook')
        debug(area)
        debug(phone)
        monkey.type(f'{areas[area]}{phone}')
        monkey.next()
        monkey.type(info["password"])
        monkey.next()
        monkey.next()
        monkey.type(info["DOB"].split(',')[0])
        monkey.next()
        monkey.type(info["DOB"].split(',')[1])
        monkey.next()
        monkey.type(info["DOB"].split(',')[2])
        monkey.next()
        monkey.next()
        monkey.right()
        monkey.enter()
        wait(3)
        code = sms.get_code()
        for i in range(100):
            if code == -1:
                wait(2)
                code = sms.get_code()
            else:
                continue
        debug(code)
        monkey.type(code)
        wait(2)
        monkey.enter()
        wait(3)
        monkey.enter()
        wait(5)
        monkey.enter()
        wait(5)
        phone_number = f'{areas[area]}{phone}'
        self.saveUser(phone_number)

    def saveUser(self, phone_number):   
        path = os.path.join(constants.USERS_PATH, 'facebook.db')
        db = sqlite3.connect(path)
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, phone TEXT)')
        cursor.execute('INSERT INTO users (id, phone) VALUES (?, ?)', (self.userId, phone_number))
        db.commit()
        

    def userExists(self):
        path = os.path.join(constants.USERS_PATH, 'facebook.db')
        db = sqlite3.connect(path)
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, phone TEXT)')
        cursor.execute('SELECT * FROM users WHERE id=?', (self.userId,))
        user = cursor.fetchone()
        if user == None:
            return False
        return True

    def getPhone(self):
        path = os.path.join(constants.USERS_PATH, 'facebook.db')
        db = sqlite3.connect(path)
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE id=?', (self.userId,))
        user = cursor.fetchone()
        if user == None:
            return None
        return user[1]

    def createUser(self, info):
        self.createUserMobile(info)
        return
        self.loadPage(Facebook.creation_url)
        sleep(3)
        monkey.click()
        monkey.next()
        monkey.type(info["firstname"])
        monkey.next()
        monkey.type(info["lastname"])
        monkey.next()
        monkey.type(info["email"])
        monkey.next()
        monkey.type(info["email"])
        monkey.next()
        monkey.type(info["password"])
        monkey.next()
        monkey.next()
        monkey.type(info["DOB"].split(',')[0])
        monkey.next()
        monkey.type(info["DOB"].split(',')[1])
        monkey.next()
        monkey.type(info["DOB"].split(',')[2])
        monkey.next()
        monkey.next()

        # if info["gender"] == 'F':
        #     monkey.press('space')
        # else:
        monkey.press('right')

        monkey.enter()
        wait(4)

        if 'confirmemail' in self.driver.current_url:
            wait(3)
            code = getMail()
            if code == -1:
                code = getMail()
            if code == -1:
                raise Exception('Could not get email code')
            monkey.type(code)
            wait(2)
            monkey.enter()
            wait(2)
            monkey.enter()

        return True

    def chromeLogin(self):
        month = random.randint(1, 12)
        day = random.randint(1, 20)
        fname = names.get_first_name()
        lname = names.get_last_name()
        email = f'{fname}_{lname}@spartaaceap.com'
        info = {'firstname': names.get_first_name(), 'lastname': names.get_last_name(), 'email': email, 'password': constants.BASIC_PASSWORD, 'DOB' : f'{month},{day},1997'}
        self.createUser(info)
        return email

    def loggedIn(self):
        self.loadPage('https://www.facebook.com/settings')
        wait(4)
        # get url of the page
        url = self.driver.current_url
        if 'login' in url:
            return False
        else:
            return True

    def getHomePage(self):
        sleep(1)
        self.driver.loadPage('https://www.facebook.com/feed')
        # home = self.driver.find_element(By.XPATH, '//a[@aria-label="Facebook"]')
        # home.click()

    def _searchTermUrl(self, term):
        search_query = Facebook.search_url % (term)
        self.loadPage(search_query)

    def _searchTermBar(self, term):
        search_bar = self._getSearchBar()
        search_bar.send_keys(term)
        sleep(3)
        search_bar.send_keys(Keys.ENTER)

    def _getSearchBar(self):
        return self.driver.find_element(By.XPATH, "//input[@placeholder='Search Facebook']")
      
    def isJoinable(self, group):
        lines = group.text

        if 'Public' not in lines:
            debug('Not public - Continue')
            return False
        button = group.find_elements(By.XPATH, './/span[text()="Join"]')
        if len(button) == 0:
            debug('Already joined - Continue')
            return False
        
        return True

    def joinCommunity(self):
        wait(1)
        communities = self.driver.find_elements(By.XPATH, '//span[text()="Groups"]')

        wait(2)
        for c in communities:
            try:
                c.click()
            except:
                pass
            wait(1)

        debug('Clicked group Button')
        wait(2)
        group = self._joinFromResults()
        return group

    def _joinFromResults(self):

        wait(2)
        results = self.driver.find_elements(By.XPATH, "//div[contains(@style, 'border-radius: max')]")

        debug(f'RESULTS: {len(results)}')

        wait(1)
        i = -1
        for result in results: 
            i += 1

            lines = result.text.split('\n')

            try:
                info = result.find_element(By.XPATH, './/a[@role="presentation"]')
            except:
                continue
            name = info.text
            group_id = info.get_attribute('href')

            members = lines[1].split('·')[1]
            members = members.replace(' members', '')
            members = convertStringToNumber(members)

            description = lines[2]

            group_info = {'name': name, 'url': group_id, 'followers': members, 'description': description, 'position': i, 'type': 'group'}

            if not self.isJoinable(result):
                continue

            join_button = result.find_element(By.XPATH, './/span[text()="Join"]')
            join_button.click()

            debug('Joined')
            group_info['Joined'] = True
            group = self.convertToSource(group_info, 'search')
            return group

        return None

    def _getUserInfo(self, url):
        self.loadPage(url)
        wait(2)
        page = dict()

        info = self.driver.find_elements(By.XPATH, f"//span[@dir='auto']")[1]

        likes = info.text.split('•')[0]
        likes = likes.split(' ')[0]
        likes = convertStringToNumber(likes)

        followers = info.text.split('•')[1]
        followers = followers.split(' ')[0]
        followers = convertStringToNumber(followers)

        page['likes'] = likes
        page['followers'] = followers
        
        return page

    def _followFirstPage(self):
        page = self.driver.find_element(By.XPATH, '//div[@aria-label="Search results"]')
        # results = page.find_elements(By.XPATH, ".//div[@style='border-radius: max(0px, min(8px, (100vw - 4px - 100%) * 9999)) / 8px;']")       
        results = self.driver.find_elements(By.XPATH, "//div[contains(@style, 'border-radius: max')]")

        position = -1
        for r in results:
            position += 1
            try:
                title = r.find_elements(By.XPATH, './/a[@role="presentation"]')
                title_text = title[0].text
            except:
                continue
            possible_buttons = r.find_elements(By.XPATH, './/div[@role="button"]')

            button = None
            for b in possible_buttons:
                if b.text == 'Follow':
                    button = b
                    break
            
            if button == None:
                info("Already following")
                continue

            url = title[0].get_attribute('href')

            button.click()
            wait(2)
            page = self._getUserInfo(url)
            page['name'] = title_text
            page['url'] = url
            page['id'] = url
            page['type'] = 'user'
            page['position'] = position
            page = self.convertToSource(page, 'search')

            debug(f"Followed {page['name']}")
            return page
        return None


    def followUser(self):
        sleep(1)
        people = self.driver.find_elements(By.XPATH, '//span[text()="Pages"]')[0]
        # people = self.driver.find_elements(By.XPATH, '//span[text()="Pages"]')[0] # For Friends
        people.click()
        sleep(2)
        page = self._followFirstPage()
        return page
        # return community

    def _processPost(self, text):
            text = text.replace('\n', ' - ')
            text = text.split('·')

            post = dict()
            if 'Suggested for you' in text[0]:
                post['suggested'] = True
                post['name'] = text[0].split('-')[1]
            else:
                post['suggested'] = False
                post['name']= text[0].split('-')[0]

            print(post)
            return

    def getPagePosts(self, n=10):
        page = self.driver.find_element(By.XPATH, '//div[@role="feed"]')
        results = page.find_elements(By.XPATH, './/div[@role="article"]')
        posts = []
        for r in results[:n+3]:
            p = self.getFeedPosts(r)
            if p == None:
                continue
            p['position'] = len(posts)
            obj = self.convertToObject(p, 'home')
            posts.append(obj)
            if len(posts)%4 == 0:
                # scroll down one page
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")

        return posts

    def convertToObject(self, post, origin):
        obj = {
            'id': post['id'],
            'platform': "facebook",
            'origin': origin,
            'position': post['position'],
            'type': post['type'],
            'source': post['source_name'],
            'secondary_source': post['source_id'],
            'likes': post['likes'],
            'comments': post['comments'],
            'shares': post['shares'],
            'views': '',
            'created_at': None,
            'title': post['title'],
            'description': None,
            'media': '',
            'url': post['id'],
            'is_ad': post['is_ad']
        }
        return obj

    def getPostInfo(self, r):
        post = dict()
        elems = r.find_elements('tag name', 'a')[0]
        if elems.get_attribute('aria-hidden') == None:
            debug('Not a post')
            return None

        is_liked = len(r.find_elements(By.XPATH, './/div[@aria-label="Remove Like"]')) > 0

        #get_all_hrefs

        hrefs = r.find_elements('tag name', 'a')
        hrefs = [href.get_attribute('href') for href in hrefs]
        hrefs = [href for href in hrefs if 'facebook.com' in href]
        post_hrefs = [href for href in hrefs if 'posts/' in href]
        photos_hrefs = [href for href in hrefs if 'photo' in href or 'video' in href]

        if len(post_hrefs) == 0:
            if len(photos_hrefs) > 0:
                href = photos_hrefs[0]
            else:
                href = ''
        else:
            href = post_hrefs[0]

        source_img = r.find_elements(By.XPATH, './/a[@aria-hidden="true"]')[0]
        element = source_img.find_element('tag name', 'a')
        source_name = element.get_attribute('aria-label')
        source_id = element.get_attribute('href').split('?')[0]

        titles = r.find_elements(By.XPATH, './/div[@data-ad-preview="message"]')
        if len(titles) > 0:
            title = titles[0].text
        else:
            title = ''

        likes = r.find_elements(By.XPATH, './/span[@aria-hidden="true"]')[-1].text
        if likes == '':
            likes = -1
        else:
            likes = convertStringToNumber(likes)


        roles = r.find_elements(By.XPATH, './/div[@role="button"]')
        comments = '-1'
        shares = '-1'
        for role in roles:
            if 'comments' in role.text:
                comments = role.text
            if 'shares' in role.text:
                shares = role.text

        comments = convertStringToNumber(comments)
        shares = convertStringToNumber(shares)

        all_links = r.find_elements(By.XPATH, './/a[@role="link"]')
        is_ad = False
        for link in all_links:
            link = link.get_attribute('href')
            if '/ads/about' in link:
                is_ad = True

        post = dict()
        post['is_liked'] = is_liked
        post['source_name'] = source_name
        post['source_id'] = source_id
        post['id'] = href
        post['title'] = title
        post['description'] = ''
        post['likes'] = likes
        post['comments'] = comments
        post['shares'] = shares
        post['created_at'] = ''
        post['media'] = ''
        post['is_ad'] = is_ad
        post['type'] = 'post'

        return post

    def pressLike(self, r):
        like_div = r.find_elements(By.XPATH, './/div[@aria-label="Like"]')
        if len(like_div) > 0:
            like_div[0].click()
            debug('Liked')

    def _isGroupPost(self, r):
        hrefs = r.find_elements('tag name', 'a')
        hrefs = [href.get_attribute('href') for href in hrefs]
        group_hrefs = [href for href in hrefs if '/groups/' in href]
        if len(group_hrefs) > 0:
            return True
        return False


    def getFeedPosts(self, r):
        post = dict()
        if len(r.find_elements('tag name', 'h4')) == 0:
            return None

        source_name = r.find_elements('tag name', 'h4')[0].text

        is_group_post = self._isGroupPost(r)

        titles = r.find_elements(By.XPATH, './/div[@data-ad-preview="message"]')
        if len(titles) > 0:
            title = titles[0].text
        else:
            title = ''

        likes = r.find_elements(By.XPATH, './/span[@aria-hidden="true"]')[-1].text
        if likes == '':
            likes = -1
        else:
            likes = convertStringToNumber(likes)


        roles = r.find_elements(By.XPATH, './/div[@role="button"]')
        comments = '-1'
        shares = '-1'
        for role in roles:
            if 'comments' in role.text:
                if 'more comments' in role.text:
                    continue
                comments = role.text
            if 'shares' in role.text:
                shares = role.text

        comments = convertStringToNumber(comments)
        shares = convertStringToNumber(shares)

        all_links = r.find_elements(By.XPATH, './/a[@role="link"]')
        is_ad = False
        for link in all_links:
            link = link.get_attribute('href')
            if '/ads/about' in link:
                is_ad = True

        
        hrefs = r.find_elements('tag name', 'a')
        hrefs = [href.get_attribute('href') for href in hrefs]
        hrefs = [href for href in hrefs if 'facebook.com' in href]
        post_hrefs = [href for href in hrefs if 'posts/' in href]
        photos_hrefs = [href for href in hrefs if 'photo' in href or 'video' in href]

        if len(post_hrefs) == 0:
            if len(photos_hrefs) > 0:
                href = photos_hrefs[0]
            else:
                href = ''
        else:
            href = post_hrefs[0]

        # ---------------------------------------------

        post['id'] = title[:8]
        post['source_name'] = source_name
        post['is_group_post'] = is_group_post
        post['title'] = title
        post['likes'] = likes
        post['comments'] = comments
        post['shares'] = shares
        post['is_ad'] = is_ad
        post['source_id'] = ''
        post['description'] = ''
        post['created_at'] = ''
        post['media'] = ''
        post['type'] = 'post'
        # if is_group_post:
        #     post['type'] = 'group_post'
        return post

    def openPost(self, already_opened=[]):
        posts_button = self.driver.find_elements(By.XPATH, './/span[text()="Posts"]')[0]       
        posts_button.click()

        page = self.driver.find_element(By.XPATH, '//div[@aria-label="Search results"]')
        wait(2)
        self.scrollDown()
        wait(1)
        self.driver.execute_script("window.scrollTo(0, 0)")       

        results = page.find_elements(By.XPATH, './/div[@role="article"]')

        i = -1
        for r in results:
            i += 1
            p = self.getPostInfo(r)
            if p == None:
                continue
            if p['is_ad']:
                continue
            if p['id'] in already_opened:
                continue
            p['position'] = i

            roles = r.find_elements(By.XPATH, './/div[@role="button"]')
            for role in roles:
                if 'comments' in role.text:
                    role.click()

            obj = self.convertToObject(p, 'results')
            return obj, [obj]
            
        error('ERROR LIKING POST')  
        return None, []


        raise NotImplementedError   


    def likePost(self):
        posts_button = self.driver.find_elements(By.XPATH, './/span[text()="Posts"]')[0]       
        posts_button.click()

        page = self.driver.find_element(By.XPATH, '//div[@aria-label="Search results"]')
        wait(2)
        self.scrollDown()
        wait(1)
        self.driver.execute_script("window.scrollTo(0, 0)")       

        results = page.find_elements(By.XPATH, './/div[@role="article"]')

        i = -1
        for r in results:
            i += 1
            p = self.getPostInfo(r)
            if p == None:
                continue

            if p['is_ad']:
                continue
            if not p['is_liked']:
                p['position'] = i
                self.pressLike(r)
                obj = self.convertToObject(p, 'results')
                return obj, []
            
        error('ERROR LIKING POST')  
        return None, []
    
    def convertToSource(self, source, origin):
        obj = {
            'id': source['url'],
            'platform': "facebook",
            'origin': origin,
            'position': source.get('position', None),
            'type': source['type'],
            'name': source.get('name', None),
            'secondary_source': source.get('secondary_source', None),
            'followers': source.get('followers', None),
            'description': source.get('description', None),
            'engagement': source.get('likes', None),
            'url': source['url'],
        }
        return obj