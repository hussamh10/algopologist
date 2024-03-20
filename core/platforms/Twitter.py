import sys
from core.account_creation.JuicySMS import juicy

from core.utils.util import convertStringToNumber;
from core.utils.log import debug
from core.utils.util import wait
from core.platforms.Platform import Platform
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from core.utils.log import *
from time import sleep
import core.utils.monkey as monkey

class Twitter(Platform):

    name = 'twitter'
    url='https://www.twitter.com'
    search_url='https://twitter.com/search?q=%s&src=typed_query'
    home_url='https://twitter.com/home'
    creation_url='https://twitter.com/i/flow/signup'

    def __init__(self, user):
        super().__init__(Twitter.name, Twitter.url, user)


    def createUserGoogle(self, profile):
        self.loadPage(Twitter.creation_url)
        sleep(3)
        monkey.next()
        monkey.next()
        monkey.space()
        sleep(3)
        monkey.type(profile['email'])
        monkey.enter()
        sleep(3)
        monkey.type(profile['password'])
        monkey.enter()
        sleep(3000)
        error('Not implemented: createUserGoogle')


    def createUser(self, profile):
        # self.createUserGoogle(profile)
        self.loadPage(Twitter.creation_url)
        # sleep(3)
        # btn = self.driver.find_element(By.XPATH, '//span[text()="Create account"]')
        # btn.click()
        # sleep(3)
        # monkey.click()
        # btn = self.driver.find_element(By.XPATH, '//input[@autocomplete="name"]')
        # btn.click()
        # sleep(2)
        # fname = profile['firstname']
        # lname = profile['lastname']
        # monkey.type(f'{fname} {lname}')
        # btn = self.driver.find_element(By.XPATH, '//span[text()="Use email instead"]')
        # btn.click()
        # sleep(1)
        # monkey.back()
        # monkey.type(profile['email'])
        # monkey.next()
        # monkey.next()
        # DOB = profile['DOB'].split(',')
        # monkey.type(DOB[0])
        # monkey.next()
        # monkey.type(DOB[1])
        # monkey.next()
        # monkey.type(DOB[2])
        # sleep(1)
        # btn = self.driver.find_element(By.XPATH, '//span[text()="Next"]')
        # btn.click()
        # sleep(2)
        # btn = self.driver.find_element(By.XPATH, '//span[text()="Next"]')
        # btn.click()
        # sleep(2)
        # btn = self.driver.find_element(By.XPATH, '//span[text()="Sign up"]')
        # btn.click()
        # sleep(10)
        monkey.email()
        return True

    def chromeLogin(self):
        wait(4)
        monkey.click(x=1800, y=234)
        wait(10)
        monkey.type('m')
        monkey.next()
        wait(1)
        monkey.type('12')
        monkey.next()
        wait(1)
        monkey.type('1993')
        wait(1)
        monkey.back()
        monkey.back()
        monkey.back()
        wait(1)
        monkey.enter()

        wait(4)
        numbers = self.driver.find_elements(By.XPATH, './/span[text()="Add a phone number"]')
        if len(numbers) > 0:
            sms = juicy()
            area, phone = sms.get_number('twitter')
            monkey.next()
            monkey.next()
            if area == 'UK':
                monkey.back()
                monkey.arrow_up()
                monkey.next()
            if area == 'NL':
                monkey.back()
                monkey.type('+31')
                monkey.next()
            monkey.type(phone)
                
            wait(1)
            monkey.next()
            monkey.enter()

            wait(1)
            monkey.enter()

            wait(3)
            code = sms.get_code()
            monkey.type(code)
            monkey.enter()
            wait(4)

        monkey.next()
        monkey.next()
        monkey.space()
        monkey.back()
        monkey.back()
        monkey.back()
        wait(1)
        monkey.enter()

        wait(3)
        self.driver.get('https://twitter.com/home')
        wait(30)


    def isAd(self, tweet):
        ads = tweet.find_elements(By.XPATH, './/span[text()="Ad"]')
        if len(ads) > 0:
            return True
        return False

    def isLiked(self, tweet):
        likeds = tweet.find_elements(By.XPATH, './/div[@data-testid="unlike"]')
        if len(likeds) > 0:
            return True
        return False

    def likable(self):
        likeds = self.driver.find_elements(By.XPATH, '//div[@aria-label="Liked"]')
        if len(likeds) > 0:
            return False
        return True

    def openPost(self, already_opened=[]):
        sleep(3)
        tweets = self.driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        num_tweets = len(tweets)
        liked = None
        for i in range(num_tweets):
            sleep(1)
            tweets = self.driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            if i >= len(tweets):
                self.scrollDown()
                sleep(2)
                self.scrollDown()
                tweets = self.driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            tweet = tweets[i]
            post = self.getPost(tweet)
            post['position'] = i
            post = self.convertToObject(post, 'search')

            if post['id'] in already_opened:
                debug('already opened')
                continue

            tweet_text = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
            tweet_text.click()
            sleep(2)
            debug('opened')
            opened = post

            if post['is_ad']:
                debug('is ad')
                continue

            back = self.driver.find_elements(By.XPATH, '//div[@aria-label="Back"]')
            if len(back) > 0:
                back[0].click()
            else:
                raise Exception('Could not find back button')

            sleep(2)
            return opened

        error("Returning last post")
        return tweets[-1]


    def likePost(self):
        sleep(3)
        tweets = self.driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        num_tweets = len(tweets)
        opened = []       
        liked = None
        for i in range(num_tweets):
            sleep(1)
            tweets = self.driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            if i >= len(tweets):
                self.scrollDown()
                sleep(2)
                self.scrollDown()
                tweets = self.driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            tweet = tweets[i]
            post = self.getPost(tweet)
            post['position'] = i
            post = self.convertToObject(post, 'search')
            tweet_text = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
            tweet_text.click()
            sleep(2)
            debug('opened')
            opened.append(post)

            if post['is_ad']:
                debug('is ad')
                continue

            if self.likable():
                like = self.driver.find_element(By.XPATH, '//div[@data-testid="like"]')
                like.click()
                liked = post.copy()
                debug('liked')
                return liked, opened

            back = self.driver.find_elements(By.XPATH, '//div[@aria-label="Back"]')
            if len(back) > 0:
                back[0].click()
            else:
                raise Exception('Could not find back button')

            sleep(2)

        return liked, opened
    
    
    def _searchTermUrl(self, term):
        search_query = Twitter.search_url % (term)
        self.loadPage(search_query)

    def _searchTermBar(self, term):
        search_bar = self._getSearchBar()
        search_bar.send_keys(term)
        sleep(3)
        search_bar.send_keys(Keys.ENTER)

    def _getSearchBar(self):
        bar = self.driver.find_element(By.XPATH, "//input[@placeholder='Search']")
        sleep(1)
        return bar


    def getHomePage(self):
        self.loadPage(Twitter.home_url)

    def isFollowed(self, user):
        following = user.find_elements(By.XPATH, './/span[text()="Following"]')
        if len(following) > 0:
            return True
        return False

    def getUserInfo(self, userFollowed):
        url = f'https://twitter.com/{userFollowed}'
        self.loadPage(url)
        wait(2)
        user = dict()
        user['id'] = userFollowed
        user['url'] = url

        followers = self.driver.find_element(By.XPATH, f'//a[@href="/{userFollowed}/verified_followers"]')
        followers = followers.text.split(' ')[0]
        followers = convertStringToNumber(followers)
        user['followers'] = followers

        username = self.driver.find_element(By.XPATH, '//div[@data-testid="UserName"]')
        user['name'] = username.text.split('\n')[0]

        try:
            description = self.driver.find_element(By.XPATH, '//div[@data-testid="UserDescription"]')
            user['description'] = description.text
        except:
            user['description'] = None
            error('Could not find description')

        return user

    def followUser(self):
        sleep(3)
        people = self.driver.find_element(By.XPATH, '//span[text()="People"]')
        people.click()
        sleep(2)

        users = self.driver.find_elements(By.XPATH, '//div[@data-testid="UserCell"]')
        
        position = -1
        for user in users:
            position += 1
            username = ''
            links = user.find_elements(By.XPATH, './/a[@role="link"]')
            for link in links:
                link = link.get_attribute('href')
                twitter_header = 'https://twitter.com'
                if twitter_header in link:
                    link = link.replace(twitter_header, '')
                print(link)
                if link.count('/') == 1:
                    username = link.replace('/', '')

            if self.isFollowed(user):
                debug(f'Already followed {username}')
                continue

            wait(2)
            follow_button = user.find_element(By.XPATH, './/span[text()="Follow"]')
            follow_button.click()
            user = self.getUserInfo(username)
            user['position'] = position
            user['type'] = 'user'
            user = self.convertToSource(user, 'search')
            return user

        raise Exception('Could not find user to follow')


    def getPost(self, tweet):
        post = dict()
        links = tweet.find_elements(By.XPATH, './/a[@role="link"]')

        for link in links:
            link = link.get_attribute('href')
            if '/analytics' in link and 'status' in link:
                if 'id' not in post:
                    post['id'] = '/'.join(link.split('/')[:-1])
                if 'username' not in post:
                    post['username'] = link.split('/')[-4]

        try:
            post['text'] = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
        except:
            post['text'] = ''
            error('Could not find text')
        post['isAd'] = self.isAd(tweet)

        group = tweet.find_element(By.XPATH, './/div[@role="group"]')
        group = group.text.split('\n')

        if len(group) != 4:
            group = tweet.find_element(By.XPATH, './/div[@role="group"]')
            group = group.text.split('\n')

        replies = tweet.find_element(By.XPATH, './/div[@data-testid="reply"]').text
        post['comments'] = convertStringToNumber(replies)
        
        retweets = tweet.find_element(By.XPATH, './/div[@data-testid="retweet"]').text
        post['retweets'] = convertStringToNumber(retweets)

        _liked = self.isLiked(tweet)
        if _liked:
            likes = tweet.find_element(By.XPATH, './/div[@data-testid="unlike"]').text
        else:
            likes = tweet.find_element(By.XPATH, './/div[@data-testid="like"]').text
        post['likes'] = convertStringToNumber(likes)

        post['views'] = convertStringToNumber(group[-1])
        
        #has video
        post['attachment'] = 'none'

        videos = tweet.find_elements(By.XPATH, './/div[@data-testid="videoComponent"]')
        if len(videos) > 0:
            post['attachment'] = 'video'

        images = tweet.find_elements(By.XPATH, './/div[@aria-label="Image"]')
        if len(images) > 0:
            post['attachment'] = 'image'

        external_links = tweet.find_elements(By.XPATH, './/a[@rel="noopener"]')
        if len(external_links) > 0:
            external_link = external_links[0].get_attribute('href')
            post['attachment'] = external_link

        return post

    def loggedIn(self):
        self.loadPage('https://twitter.com/messages')
        wait(4)
        # get url of the page
        url = self.driver.current_url
        if 'login' in url:
            return False
        else:
            return True

    def getPagePosts(self, n):
        tweets = self.driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        posts = []
        for i, tweet in enumerate(tweets):
            try:
                post = self.getPost(tweet)
            except:
                error('Could not get post')
                continue
            post['position'] = i
            posts.append(post)

        return posts


    def convertToObject(self, post, origin):
        obj = {
            'id': post['id'],
            'platform': "twitter",
            'origin': origin,
            'position': post.get('position', None),
            'type': 'post',
            'source': post.get('username', None),
            'secondary_source': None,
            'likes': post.get('likes', None),
            'comments': post.get('comments', None),
            'shares': post.get('retweets', None),
            'views': post.get('views', None),
            'created_at': post.get('created_at', None),
            'title': post.get('text', ''),
            'description': post.get('description', ''),
            'media': post.get('attachment', None),
            'url': post.get('id', None),
            'is_ad': post.get('isAd', False)
        }
        return obj

    def isJoined(self, l):
        joined = l.find_elements(By.XPATH, './/div[@aria-label="Following"]')
        if len(joined) > 0:
            return True
        return False


    def joinCommunity(self):
        sleep(3)
        people = self.driver.find_elements(By.XPATH, '//span[text()="Lists"]')[1]
        people.click()
        sleep(2)

        lists = self.driver.find_elements(By.XPATH, '//div[@data-testid="listCell"]')
        
        for l in lists:
            text = l.text.split('\n')
            for i in text:
                debug(i)

            listname = text[0]

            if self.isJoined(l):
                debug(f'Already followed {listname}')
                continue

            join_button = l.find_element(By.XPATH, './/div[@aria-label="Follow"]')
            join_button.click()
            debug(f'Followed {listname}')
            return listname

        raise Exception('Could not find list to join')

    def convertToSource(self, source, origin):
        obj = {
            'id': source['id'],
            'platform': "twitter",
            'origin': origin,
            'position': source.get('position', None),
            'type': source['type'],
            'name': source.get('name', None),
            'secondary_source': source.get('secondary_source', None),
            'followers': source.get('followers', None),
            'description': source.get('description', None),
            'engagement': source.get('engagement', None),
            'url': source['url'],
        }
        return obj
