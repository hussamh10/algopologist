from time import sleep, time
import pandas as pd
import sqlite3
from uuid import uuid4 as uid
import os
from core.constants import *
from core.utils.util import wait; 
from core.utils.log import debug, info, error

class User:
    def __init__(self, platform, chromeId, experiment_id):
        self.Platform = platform
        self.userId = chromeId
        self.chromeId = chromeId
        self.experiment_id = experiment_id
        self.info = {'platform': self.Platform.__name__, 'id': self.chromeId}
        pass


    def _addSource(self, source):
        conn = sqlite3.connect(DATABASE)
        ouid = str(uid())[:8]
        c = conn.cursor()
        source['description'] = source.get('description', '').replace("'", "")
        source['name'] = source.get('name', '').replace("'", "")
        source['url'] = source.get('url', '').replace("'", "")
        source['secondary_source'] = source.get('secondary_source', '').replace("'", "")

        debug("INSERT INTO sources VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % ( ouid, source['id'], source['platform'], source['origin'], source['position'], source['type'], source['name'], source['secondary_source'], source['followers'], source['description'], source['engagement'], source['url']))
        c.execute("INSERT INTO sources VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            ouid, source['id'], source['platform'], source['origin'], source['position'], source['type'], source['name'], source['secondary_source'], source['followers'], source['description'], source['engagement'], source['url']
        ))
        conn.commit()
        conn.close()
        return ouid

    def _addPost(self, obj):
        conn = sqlite3.connect(DATABASE)
        ouid = str(uid())[:8]
        obj['description'] = obj.get('description', '').replace("'", "")
        obj['description'] = obj.get('description', '').replace('"', "")
        obj['name'] = obj.get('name', '').replace("'", "")
        obj['name'] = obj.get('name', '').replace('"', "")
        obj['url'] = obj.get('url', '').replace("'", "")
        obj['source'] = obj.get('source', '').replace("'", "")
        # info(f"INSERT INTO posts VALUES ('{ouid}', '{obj['id']}', '{obj['platform']}', '{obj['origin']}', '{obj['position']}', '{obj['type']}', '{obj['source']}', '{obj['secondary_source']}', '{obj['likes']}', '{obj['comments']}', '{obj['shares']}', '{obj['views']}', '{obj['created_at']}', '{obj['title']}', '{obj['description']}', '{obj['media']}', '{obj['url']}', '{obj['is_ad']}')")
        insert = f"INSERT INTO posts VALUES ('{ouid}', '{obj['id']}', '{obj['platform']}', '{obj['origin']}', '{obj['position']}', '{obj['type']}', '{obj['source']}', '{obj['secondary_source']}', '{obj['likes']}', '{obj['comments']}', '{obj['shares']}', '{obj['views']}', '{obj['created_at']}', '{obj['title']}', '{obj['description']}', '{obj['media']}', '{obj['url']}', '{obj['is_ad']}')"
        c = conn.cursor()
        c.execute(insert)
        conn.commit()
        conn.close()
        return ouid

    def addSignal(self, action, object, object_type, info=''):
        try:
            if object_type == 'source':
                object_uid = self._addSource(object)
            elif object_type == 'post':
                object_uid = self._addPost(object)
            else:
                object_uid = object
        except Exception as e:
            error(f'Error adding object: {e}')
            object_uid = ''

        signal_id = str(uid())[:8]
        screenshot = f'{action}-{signal_id}.png'
        print(SCREENSHOTS_PATH, self.experiment_id, self.chromeId, self.Platform.__name__, action, signal_id)
        path = os.path.join(SCREENSHOTS_PATH, self.experiment_id)
        if not os.path.exists(path):
            os.makedirs(path)
        platform_name = self.Platform.__name__
        screenshot = os.path.join(path, self.chromeId, platform_name, screenshot)
        self.takeScreenshot(screenshot)

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO signals VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            signal_id, action, object_uid, screenshot, int(time()), self.chromeId, self.Platform.__name__, info, self.experiment_id 
        ))
        conn.commit()
        conn.close()
        debug('Signal added: %s' % action)

    def checkSignin(self):
        debug(f'SIGNING IN: {self.chromeId}')
        self.platform = self.Platform(self.chromeId)
        self.platform.loadBrowser()
        self.platform.loadWebsite()
        is_signedin =  self.platform.loggedIn()
        return is_signedin

    def chromeSignIn(self):
        debug(f'SIGNING IN: {self.chromeId}')
        self.platform = self.Platform(self.chromeId)
        self.platform.loadBrowser()
        self.platform.loadWebsite()
        wait(2)

    def chromeSignUp(self):
        self.platform = self.Platform(self.chromeId)
        self.platform.loadBrowser()
        self.platform.loadWebsite()
        wait(4)
        email = self.platform.chromeLogin()
        debug('Email: %s' % email)
        self.addSignal('create', email, 'user', info=self.chromeId)
        wait(7)
  
    def followUser(self, topic):
        wait(2)
        self.goHome()
        wait(2)
        self.search(topic)
        debug('Term searched')
        user = self.platform.followUser()
        self.addSignal('follow', user, 'source', info=f'searched-{topic}')
        wait(3)
        pass

    def getOpenedPosts(self):
        conn = sqlite3.connect(DATABASE)
        signals = pd.read_sql_query("SELECT * FROM signals WHERE action = 'open' AND user = '%s'" % (self.info['id']), conn)
        posts = pd.read_sql_query("SELECT * FROM posts WHERE platform = '%s'" % (self.info['platform']), conn)
        df = pd.merge(signals, posts, left_on='object_id', right_on='id')
        conn.close()
        posts = list(df['post_id'])
        return posts

    def openPost(self, topic):
        info(f"Opeining post for {topic}")
        sleep(2)
        self.search(topic)
        opened_posts = self.getOpenedPosts()
        post, opened = self.platform.openPost(already_opened=opened_posts)
        self.addSignal('open', post, 'post', info=f'searched-{topic}')
        debug(f"OPENED POST: {post['id']}")
        return post

    def likePost(self, topic):
        wait(2)
        self.goHome()
        wait(2)
        self.search(topic)
        info('Term searched: %s' % topic)
        post, opened = self.platform.likePost()
        path = f'{post["id"]}.png'

        print(post)

        if post == None:
            error('No post found to like')
            raise Exception('No post found to like')

        for open in opened:
            self.addSignal('open', open, 'post', info=f'searched-{topic}')

        if post != None:
            self.addSignal('like', post, 'post', info=f'searched-{topic}')

        return post
  
    def joinCommunity(self, topic,):
        wait(2)
        self.goHome()
        wait(2)
        self.search(topic)
        debug('Term searched')
        community = self.platform.joinCommunity()
        self.addSignal('join', community, 'source', info=f'searched-{topic}')
        pass

    def getPosts(self, scrolls, posts_n=10):
        posts = []
        
        if self.platform.name == 'facebook':
            for i in range(scrolls):
                self.platform.scrollDown()
                wait(1)
            self.platform.scrollTop()
            posts = self.platform.getPagePosts(posts_n+5)
            return posts
        
        for i in range(scrolls):
            self.platform.scrollDown()
            posts += self.platform.getPagePosts(posts_n)
            sleep(2)
        return posts

    def recordHome(self, scrolls=5):
        self.goHome()
        sleep(2)
        posts = self.getPosts(scrolls)
        uuid = str(uid())[:8]
        image_name = f'{self.userId}-{self.experiment_id}-{self.platform.name}-{uuid}.png'
        self.takeScreenshot(image_name)
        return posts, image_name

    def goHome(self):
        try:
            self.platform.getHomePage()
        except Exception as e:
            self.platform.loadWebsite()
        wait(3.2)

    def search(self, key):
        self.platform.searchTerm(key)
        self.addSignal('search', None, '', info=f'searched-{key}')

    def scrollDown(self, num=1):
        for i in range(num):
            self.platform.scrollDown()

    def takeScreenshot(self, file):
        path = os.path.join(SCREENSHOTS_PATH, file)
        self.platform.screenshot(path)

    def closeDriver(self):
        self.platform.closeDriver()