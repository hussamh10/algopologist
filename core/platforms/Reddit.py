from tqdm import tqdm
from core.utils.util import wait
from core.utils.log import *
import core.constants as constants
import core.utils.monkey as monkey
from core.platforms.Platform import Platform
from core.constants import CONTINUE_GOOGLE_X, CONTINUE_GOOGLE_Y

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import sqlite3 as sql
import os
import praw
import core.constants as core

class RedditPRAW():

    def __init__(self):
        self.reddit_client = praw.Reddit(
            client_id=constants.PRAW['client_id'],
            client_secret=constants.PRAW['client_secret'],
            user_agent=constants.PRAW['user_agent'],
        )

        self.db_path = os.path.join(constants.DATA_DIR, 'praw.db')
        
    def isPostInDB(self, id):
        db = sql.connect(self.db_path)
        query = f"SELECT * FROM posts WHERE id='{id}'"
        res = db.execute(query).fetchall()
        db.close()
        if len(res) == 0:
            return False
        else:
            return True

    def isArchived(self, id):
        submission = self.reddit_client.submission(id)
        return submission.archived

    def addPostToDB(self, post):
        post['title'] = post['title'].replace("'", "")
        post['selftext'] = post['selftext'].replace("'", "")

        query = f"INSERT INTO posts VALUES ('{post['id']}', '{post['title']}', '{post['author']}', '{post['subreddit']}', '{post['num_comments']}', '{post['score']}', '{post['selftext']}', '{post['url']}', '{post['created_at']}')"
        db = sql.connect(self.db_path)
        db.execute(query)
        db.commit()
        db.close()

    def getPostFromDB(self, id):
        query = f"SELECT * FROM posts WHERE id='{id}'"
        db = sql.connect(self.db_path)
        res = db.execute(query).fetchall()
        if len(res) == 0:
            raise Exception('Post not in DB')
        else:
            res = res[0]
            post = dict()
            post['id'] = res[0]
            post['title'] = res[1]
            post['author'] = res[2]
            post['subreddit'] = res[3]
            post['num_comments'] = res[4]
            post['score'] = res[5]
            post['selftext'] = res[6]
            post['url'] = res[7]
            post['created_at'] = res[8]
            return post
        
    def getPost(self, id):
        if self.isPostInDB(id):
            post = self.getPostFromDB(id)
            return post
    
        res = dict()
        try:
            submission = self.reddit_client.submission(id)
            res['id'] = id
            res['title'] = submission.title
            if submission.author is None:
                res['author'] = '[deleted]'
            else:
                res['author'] = submission.author.name
            res['subreddit'] = submission.subreddit.display_name
            res['num_comments'] = submission.num_comments
            res['score'] = submission.score
            res['selftext'] = submission.selftext
            res['url'] = submission.url
            res['created_at'] = submission.created_utc
        except Exception as e:
            error(e)
            error('ERROR GETTING POST FROM PRAW')
            res['id'] = ''
            res['title'] = ''
            res['author'] = ''
            res['subreddit'] = ''
            res['num_comments'] = ''
            res['score'] = ''
            res['selftext'] = ''
            res['url'] = ''
            res['created_at'] = ''

        self.addPostToDB(res)

        return res
    
    def getSubreddit(self, name):
        res = dict()
        try:
            subreddit = self.reddit_client.subreddit(name)
            res['name'] = subreddit.display_name
            res['members'] = subreddit.subscribers
            res['description'] = subreddit.public_description
            res['url'] = subreddit.url
        except Exception as e:
            error(e)
            error('ERROR GETTING SUBREDDIT FROM PRAW')
            res['name'] = ''
            res['members'] = ''
            res['description'] = ''
            res['url'] = ''
        return res
    
    def getUser(self, name):
        res = dict()
        try:
            user = self.reddit_client.redditor(name)
            res['name'] = user.name
            res['engagement'] = user.link_karma
            res['url'] = name
        except Exception as e:
            error(e)
            error('ERROR GETTING USER FROM PRAW')
            res['name'] = ''
            res['engagement'] = ''
            res['url'] = ''
        return res

class Reddit(Platform):
    name = 'reddit'
    url='https://new.reddit.com'
    search_url='https://new.reddit.com/search/?q=%s'
    creation_url='https://new.reddit.com/register/'

    def __init__(self, userId):
        super().__init__(Reddit.name, Reddit.url, userId)

    def loadWebsite(self):
        super().loadWebsite()
        # check if aria-label='Close' is present
        # if it is, click it
        # if not, continue

        wait(5)
        if len(self.driver.find_elements(By.XPATH, '//button[@aria-label="Close"]')):
            self.driver.find_element(By.XPATH, '//button[@aria-label="Close"]')

    def loggedIn(self):
        self.loadPage('https://www.reddit.com/settings/')
        wait(4)
        # get url of the page
        url = self.driver.current_url
        if 'login' in url:
            return False
        else:
            return True

    def _searchTermUrl(self, term):
        search_query = Reddit.search_url % (term)
        self.loadPage(search_query)
        wait(2)

    def _searchTermBar(self, term):
        wait(2.2)
        search_bar = self._getSearchBar()
        if search_bar is None:
            error('Search bar not found')
            debug('Searching by URL')
            self._searchTermUrl(term)
            return

        search_bar.send_keys(term)
        wait(1)
        search_bar.send_keys(Keys.ENTER)

    def _getSearchBar(self):
        try: 
            search = self.driver.find_element(By.ID, "header-search-bar")
        except:
            try:
                search = self.driver.find_element(By.XPATH, "//input[@placeholder='Search Reddit']")
            except:
                search = None
        
        return search

    def _getPostsResults(self):
        results = self.driver.find_element(By.XPATH, "//div[@data-testid='posts-list']")
        results = results.find_elements(By.XPATH, "//div[@data-testid='post-container']")
        
        posts = []
        for i, result in enumerate(results):
            post = dict()
            post['position'] = i
            post['id'] = result.get_attribute('id')
            post['elem'] = result
            posts.append(post)

        return posts

    def _getCommunityResults(self):
        results = self.driver.find_element(By.XPATH, "//div[@data-testid='communities-list']")
        results = results.text
        lines = results.split('\n')

        c = []
        data = []
        i = 0
        for line in lines:
            c.append(line)
            i+=1 
            if i % 4 == 0:
                data.append(c)
                c = []

        subreddits = dict()
        i = 1
        for c in data:
            subreddits[c[0]] = {'Rank': i, 'Members': c[1], 'Description': c[2], 'Joined': c[3]}
            status = c[3]
            if status == 'Join':
                subreddits[c[0]]['Joined'] = False
            else:
                subreddits[c[0]]['Joined'] = True
            i += 1

        results = {'subreddits': subreddits}
        return results

    def _getPeopleResults(self):
        results = self.driver.find_element(By.XPATH, "//div[@data-testid='people-list']")
        results = results.text
        lines = results.split('\n')
        c = []
        data = []
        i = 0
        for line in lines:
            c.append(line)
            i+=1 
            if i % 4 == 0:
                data.append(c)
                c = []

        people = dict()
        i = 1
        for c in data:
            people[c[0]] = {'Rank': i, 'Karma': c[1], 'Description': c[2], 'Followed': c[3]}
            status = c[3]
            if status == 'Follow':
                people[c[0]]['Followed'] = False
            else:
                people[c[0]]['Followed'] = True
            i += 1

        results = {'people': people}
        return results

    def _joinNthSubreddit(self, N=0):
        wait(1)
        profiles = self.driver.find_elements(By.XPATH, '//a[@data-testid="subreddit-link"]')
        position = 0
        for i in profiles:
            if 'Joined' not in i.text:
                if 'Join' in i.text:
                    community = i.get_attribute('href')[:-1].split('/')[-1]
                    join = i.find_element(By.XPATH, '//button[text()="Join"]')
                    debug(community)
                    join.click()
                    break
            position += 1
        api = RedditPRAW()
        subreddit = api.getSubreddit(community)
        subreddit['position'] = position
        subreddit['type'] = 'community'
        subreddit = self.convertToSource(subreddit, 'search')
        return subreddit

    def _joinNthUser(self, N=0):
        wait(1)
        profiles = self.driver.find_elements(By.XPATH, '//a[@data-testid="profile-link"]')
        position = 0
        for i in profiles:
            if 'Following' not in i.text:
                if 'Follow' in i.text:
                    user = i.get_attribute('href')
                    follow = i.find_element(By.XPATH, '//button[text()="Follow"]')
                    debug(user)
                    follow.click()
                    break
            position += 1
        api = RedditPRAW()
        if 'user/' in user:
            user = user.split('user/')[1] 
            if '/' in user:
                user = user.split('/')[0]
        user = api.getUser(user)
        user['position'] = position
        user['type'] = 'user'
        user = self.convertToSource(user, 'search')
        return user

    def followUser(self):
        wait(1)
        people = self.driver.find_element(By.XPATH, '//button[text()="People"]')
        people.click()
        wait(2)
        self._getPeopleResults()
        user = self._joinNthUser(0)
        return user
        
    def joinCommunity(self):
        wait(1)
        communities = self.driver.find_element(By.XPATH, '//button[text()="Communities"]')
        communities.click()
        wait(2)
        self._getCommunityResults()
        community = self._joinNthSubreddit(0)
        return community

    def getHomePage(self):
        wait(1)
        home = self.driver.find_element(By.XPATH, '//a[@aria-label="Home"]')
        home.click()

    def _getPostId(self, links):
        ids = []
        for link in links:
            link = link.split('/comments/')[1].split('/')[0]
            ids.append(link)
        return ids

    def _getPostInfo(self, id):
        api = RedditPRAW()
        id = id.split('_')[1]
        try:
            post = api.getPost(id)
        except Exception as e:
            error(str(e))
            error('ERROR GETTING POST FROM PRAW')
            post = {'id': id, 'title': '', 'author': '', 'subreddit': '', 'num_comments': '', 'score': '', 'selftext': '', 'url': ''}
        return post

    def getPagePosts(self, n=10):
        wait(1)
        posts = self.driver.find_elements(By.XPATH, '//div[@data-testid="post-container"]')

        posts_urls = []

        for post in posts:
            try:
                url = post.find_element(By.XPATH, './/a[@data-click-id="body"]').get_attribute('href')           
                posts_urls.append(url)
            except:
                pass

        posts_ids = self._getPostId(posts_urls)
        posts = []

        api = RedditPRAW()

        i = 0
        for post in tqdm(posts_ids):
            post = api.getPost(post)
            post['position'] = i
            post = self.convertToObject(post, 'home')
            posts.append(post)
            i += 1

        return posts
    
    def openPost(self, already_opened=[]):
        wait(2)
        posts = self.driver.find_element(By.XPATH, '//button[text()="Posts"]')
        posts.click()
        wait(1)
        posts = self._getPostsResults()
        debug("Posts: " + str(len(posts)))
        
        for post in posts:
            wait(0.3)
            if post['id'] in already_opened:
                debug('Already opened: ' + post['id'])
            else:
                post['elem'].click()
                wait(2)
                post_info = self._getPostInfo(post['id'])
                post_info['position'] = post['position']
                post_info = self.convertToObject(post_info, 'search')
                return post_info
        wait(1)
        error("Returning last post")
        post = posts[-1]
        post_info = self._getPostInfo(post['id'])
        post_info['position'] = post['position']
        return post_info

    def likable(self, id):
        api = RedditPRAW()
        id = id.split('_')[-1]
        try:
            if api.isArchived(id):
                return False
            else:
                return True
        except Exception as e:
            error('ERROR GETTING POST FROM PRAW')
            return False
        
    def likePost(self):
        posts = self.driver.find_element(By.XPATH, '//button[text()="Posts"]')
        posts.click()
        wait(1)
        posts = self._getPostsResults()
        opened = []
        
        for i, post in enumerate(posts):
            wait(2)
            if not self.likable(post['id']):
                continue
            post['elem'].click()
            post_info = self._getPostInfo(post['id'])
            post_info['position'] = i
            opened.append(post_info)
            wait(2)
            dislike = self.driver.find_element(By.XPATH, '//button[@aria-label="downvote"]')
            like = self.driver.find_element(By.XPATH, '//button[@aria-label="upvote"]')
            if dislike.get_attribute('aria-pressed') == 'true':
                debug('already disliked')
                close = self.driver.find_element(By.XPATH, '//button[@aria-label="Close"]')
                close.click()
            elif like.get_attribute('aria-pressed') == 'true':
                debug('already liked')
                close = self.driver.find_element(By.XPATH, '//button[@aria-label="Close"]')
                close.click()
            else:
                if self.likable(post['id']):
                    like.click()
                    debug(f"liked post {post['id']}")
                    post_info = self.convertToObject(post_info, 'search')
                    opened = [self.convertToObject(p, 'search') for p in opened]
                    return post_info, opened
        
        error('ERROR LIKING POST')
        opened = [self.convertToObject(p, 'search') for p in opened]
        return None, opened

    def convertToObject(self, post, origin):
        obj = {
            'id': post['id'],
            'platform': "reddit",
            'origin': origin,
            'position': post['position'],
            'type': 'post',
            'source': post['author'],
            'secondary_source': post['subreddit'],
            'likes': post['score'],
            'comments': post['num_comments'],
            'shares': None,
            'views': None,
            'created_at': post['created_at'],
            'title': post['title'],
            'description': post['selftext'],
            'media': None,
            'url': post['url'],
            'is_ad': None
        }
        return obj

    def convertToSource(self, source, origin):
        obj = {
            'id': source['name'],
            'platform': "reddit",
            'origin': origin,
            'position': source.get('position', None),
            'type': source['type'],
            'name': source.get('name', None),
            'secondary_source': source.get('secondary_source', None),
            'followers': source.get('members', None),
            'description': source.get('description', None),
            'engagement': source.get('engagement', None),
            'url': source['url'],
        }
        return obj

    def chromeLogin(self):
        try:
            wait(1)
            monkey.click(x=CONTINUE_GOOGLE_X, y=CONTINUE_GOOGLE_Y)
        except Exception as e:
            print(e)
            pass
        wait(15)
        self.loadWebsite()
        wait(15)
        return f'{self.userId}@spartaaceap.com'