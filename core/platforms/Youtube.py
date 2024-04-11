import sys

from core.utils.util import convertStringToNumber, wait;
from core.platforms.Platform import Platform
from core.utils.log import *

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from innertube import InnerTube

class MyTube():
    def __init__(self):
        self.tube = InnerTube("WEB")
        
    def getChannelInfo(self, channel_id):
        PARAMS_TYPE_CHANNEL = "EgIQAg%3D%3D"
        data = self.tube.search(channel_id, params=PARAMS_TYPE_CHANNEL)

        channels = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
        for channel in channels:
            if 'channelRenderer' not in channel:
                continue
            channel = channel['channelRenderer']
            break

        name = channel['title']['simpleText']
        id = channel['channelId']
        try:
            runs = channel['descriptionSnippet']['runs']
            description = [i['text'] for i in runs]
            description = ''.join(description)
            subscribers = channel['videoCountText']['simpleText']
            subscribers = convertStringToNumber(subscribers)
        except Exception as e:
            description = ''
            subscribers = 0

        channel = {
            'name': name,
            'urlId': channel_id,
            'id': id,
            'description': description,
            'subscribers': subscribers
        }
        return channel

    def getVideoInfo(self, video_id):
        try:    
            data = self.tube.player(video_id=video_id)
            try:
                publish_date = data['microformat']['playerMicroformatRenderer']['uploadDate']
            except Exception as e:
                publish_date = None
            data = data['videoDetails']
            video = dict()
            video['id'] = video_id
            video['title'] = data['title']
            video['channel'] = data['author']
            video['length'] = data['lengthSeconds']
            video['views'] = data['viewCount']
            video['url'] = f"https://www.youtube.com/watch?v={video_id}"
            video['created'] = publish_date
            video['description'] = data['shortDescription']

            try:
                client = InnerTube("WEB")
                data = client.next(video_id)
                like_count = data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][0]["videoPrimaryInfoRenderer"]["videoActions"]["menuRenderer"]["topLevelButtons"][0]["segmentedLikeDislikeButtonRenderer"]["likeButton"]["toggleButtonRenderer"]["defaultText"]["accessibility"]["accessibilityData"]["label"].split(" ")[0]
                like_count = int(like_count.replace(",", ""))
                comment_count = data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][2]['itemSectionRenderer']['contents'][0]['commentsEntryPointHeaderRenderer']['commentCount']['simpleText']
                comment_count = convertStringToNumber(comment_count)

            except Exception as e:
                like_count = None
                comment_count = None
            finally:
                video['likes'] = like_count
                video['comments'] = comment_count

            return video
        except Exception as e:
            error('InnerTube error')
            error(f"{e}: {video_id}")
            video = {'id': video_id, 'title': '', 'channel': '', 'length': '', 'views': ''}
            return video

class Youtube(Platform):
    name = 'youtube'
    url='https://www.youtube.com'
    search_url='https://www.youtube.com/results?search_query=%s'

    def __init__(self, user):
        super().__init__(Youtube.name, Youtube.url, user)

    def createUser(self, profile):
        pass

    def _searchTermUrl(self, term):
        search_query = Youtube.search_url % (term)
        self.loadPage(search_query)

    def _searchTermBar(self, term):
        search_bar = self._getSearchBar()
        debug(search_bar)
        search_bar.send_keys('')
        wait(1)
        search_bar.send_keys(term)
        wait(1)
        search_bar.send_keys(Keys.ENTER)

    def _getSearchBar(self):
        return self.driver.find_element(By.XPATH, "//input[@placeholder='Search']")

    def loggedIn(self):
        debug('Checking if logged in')
        self.loadPage('https://www.youtube.com/account')
        wait(4)
        # get url of the page
        url = self.driver.current_url
        debug(f"Checking if logged in: {url}")
        if 'login' in url:
            return False
        else:
            return True

    def getHomePage(self):
        home = self.driver.find_element(By.XPATH, '//a[@title="YouTube Home"]')
        home.click()
        wait(2)

    def pauseHistory(self):
        debug('Turning offf history')
        self.driver.get('https://www.youtube.com/feed/history')
        wait(2)
        try:
            button = self.driver.find_element(By.XPATH, '//button[@aria-label="Pause watch history"]')
            button.click()
            wait(1)
            button = self.driver.find_element(By.XPATH, '//button[@aria-label="Pause"]')
            button.click()
            wait(1)
        except Exception as e:
            debug('Already turned on history')
            pass

    def getRecommendations(self, post):
        video_link = f"https://www.youtube.com/watch?v={post}"
        self.loadPage(video_link)
        wait(30)
        if self.isAd():
            self._handleAd()

        wait(30)

        recommendations = self.driver.find_elements(By.XPATH, '//a[@class="yt-simple-endpoint style-scope ytd-compact-video-renderer"]')
        r = [recommendation.get_attribute('href').split('?v=')[1] for recommendation in recommendations if recommendation.get_attribute('href')]

        return r

    def followUser(self, channel=None, name=None):
        self.openChannelResults()
        wait(2)
        tube = MyTube()

        tag = 'ytd-channel-renderer'
        channels = self.driver.find_elements(By.XPATH, f'//{tag}')
        position = -1

        for channel in channels:
            position += 1
            if 'Subscribed' in channel.text:
                position +=1
                continue

            tag = 'a'
            hrefs = channel.find_elements(By.XPATH, f'.//{tag}')
            hrefs = [href.get_attribute('href') for href in hrefs]

            channel_id = hrefs[0].split('@')[-1]

            tag = 'button'
            buttons = channel.find_elements(By.XPATH, f'.//{tag}')

            subscribed = False
            for button in buttons:
                if 'Subscribe' in button.text:
                    button.click()
                    print('subscribed')
                    subscribed = True
                    break

            if subscribed:
                channel = dict()
                channel = tube.getChannelInfo(channel_id)
                channel['type'] = 'user'
                channel['position'] = position
                return channel           

            position += 1


        # channels = self.driver.find_elements(By.XPATH, '//div[@id="content-section"]')
        # position = -1
        # for channel in channels:
        #     position += 1
        #     # check if subscribed
        #     try:
        #         channel_id = channel.find_element(By.XPATH, './/span[@id="subscribers"]')
        #         channel_id = channel_id.text

        #         subscribe_button = channel.find_elements(By.XPATH, './/div[@id="subscribe-button"]')
        #         debug(channel_id)
        #         if len(subscribe_button) == 0:
        #             error('No subscribe button found...: ' + channel_id)
        #             continue

        #         text = subscribe_button[0].text
        #         if text == 'Subscribed':
        #             debug('Already subscribed...: ' + channel_id)
        #             continue
        #         elif text == 'Subscribe':
        #             subscribe_button[0].click()
        #             channel = tube.getChannelInfo(channel_id)
        #             channel['type'] = 'user'
        #             channel['position'] = position
        #             debug('Subscribed: ' + channel['name'])
        #             wait(1)
        #             channel = self.convertToSource(channel, 'search')
        #             return channel
        #         else:
        #             error('Unknown subscribe button text...: ' + channel_id)
        #             continue
        #     except Exception as e:
        #         error('Error')
        #         continue

    def openChannelResults(self):
        wait(1)
        filters = self.driver.find_element(By.XPATH, '//button[@aria-label="Search filters"]')
        filters.click()
        wait(1)
        channels = self.driver.find_element(By.XPATH, '//yt-formatted-string[text()="Channel"]')
        channels.click()

    def joinCommunity(self):
        raise Exception("No communities in Youtube")

    def getIdfromUrl(self, url):
        if "&" in url:
            url = url.split('&')[0]
        if 'v=' in url:
            url = url.split('v=')[1]
        return url


    def _getPostsResults(self):
        wait(3)
        results = self.driver.find_elements(By.TAG_NAME, "ytd-video-renderer")
        videos = []
        for i, res in enumerate(results):
            video = dict()
            video['position'] = i
            video['name'] = res.find_element(By.ID, 'video-title').text
            is_short = res.find_elements(By.XPATH, './/*[@aria-label="Shorts"]')
            if len(is_short) > 0:
                debug('Short video, skipping...')
                continue
            url = res.find_element(By.ID, 'video-title').get_attribute('href')
            video['id'] = self.getIdfromUrl(url)
            elem = res.find_element(By.ID, 'video-title')
            video['elem'] = elem
            videos.append(video)

        return videos


    def turnOnHistory(self):
        debug('Turning on history')
        self.driver.get('https://www.youtube.com/feed/history')
        wait(2)
        try:
            button = self.driver.find_element(By.XPATH, '//button[@aria-label="Turn on watch history"]')
            button.click()
            wait(1)
            button = self.driver.find_element(By.XPATH, '//button[@aria-label="Turn on"]')
            button.click()
            wait(1)
        except Exception as e:
            debug('Already turned on history')
            pass

    def addToHistory(self, video):
        video_link = f"https://www.youtube.com/watch?v={video}"
        self.loadPage(video_link)

        if self.isAd():
            self._handleAd()
        wait(10)

    def getPagePosts(self, posts_n=30):
        video_elems = self.driver.find_elements(By.XPATH, '//a[@id="video-title-link"]')
        tube = MyTube()

        videos = []
        ids = []
        for i, elem in enumerate(video_elems):
            video = dict()
            video['id'] = elem.get_attribute('href').split('v=')[1]
            video_info = tube.getVideoInfo(video['id'])
            video_info['position'] = i
            video = self.convertToObject(video_info, 'home')
            if video['id'] in ids:
                continue
            ids.append(video['id'])
            videos.append(video)
        return videos

    def getPost(self, video):
        self.loadPage(video['url'])
        wait(2)
        video['id'] = self.driver.current_url.split('v=')[1]
        return video

    def isAd(self):
        try:
            self.driver.find_element(By.XPATH, '//div[@class="ytp-ad-text"]') # Detect if there is an ad.
            return True
        except Exception:
            return False

    def openPost(self, already_opened=[]):
        videos = self._getPostsResults()
        tube = MyTube()
        wait(2)
        opened = []
        #select first video
        video = videos[0]
        video['elem'].click()
        video_info = tube.getVideoInfo(video['id'])
        opened.append(video_info)
        wait(3)
        if self.isAd():
            self._handleAd()
        debug('Watching video for 30 seconds')
        wait(30)
        return video_info

    def likeable(self):
        # check if likeable
        like_buttons = self.driver.find_elements(By.TAG_NAME, "ytd-video-renderer")
        like_button = like_buttons[0]
        # get title of button inside element
        unlikes = like_button.find_elements(By.XPATH, '//button[@title="Unlike"]')
        likes = like_button.find_elements(By.XPATH, '//button[@title="I like this"]')
        if len(likes) > 0:
            return True
        if len(unlikes) > 0:
            return False
        error('No like buttons found')
        return True


    def likePost(self):
        videos = self._getPostsResults()
        tube = MyTube()
        wait(2)
        opened = []
        position = -1
        for v in range(len(videos)):
            position += 1
            video = videos[v]
            video['elem'].click()
            video_info = tube.getVideoInfo(video['id'])
            video_info['position'] = position
            video = self.convertToObject(video_info, 'search')
            opened.append(video)
            wait(3)
            if self.isAd():
                debug('Handling ad')
                self._handleAd()
            if self.likeable():
                like_buttons = self.driver.find_elements(By.TAG_NAME, "ytd-video-renderer")
                like_button = like_buttons[0]
                like = like_button.find_elements(By.XPATH, '//button[@title="I like this"]')[0]
                debug('Watching video for 30 seconds')
                wait(30)
                like.click()
                wait(3)
                return video, opened
            else:
                debug('Already liked')
                self.driver.back()
                wait(3)

        return None, opened

    def convertToObject(self, post, origin):
        obj = {
            'id': post['id'],
            'platform': "youtube",
            'origin': origin,
            'position': post.get('position', None),
            'type': 'post',
            'source': post.get('channel', ''),
            'secondary_source': None,
            'likes': post.get('likes', ''),
            'comments': post.get('comments', ''),
            'shares': None,
            'views': post.get('views', ''),
            'created_at': post.get('created', ''),
            'title': post.get('title', ''),
            'description': post.get('description', ''),
            'media': None,
            'url': post.get('url', ''),
            'is_ad': None,
        }
        
        return obj

    def _handleAd(self):
        while True:
            try:
                self.driver.find_element(By.XPATH, '//div[@class="ytp-ad-text"]') # Detect if there is an add.
            except Exception:
                return   # Return in case there is no ad
            wait(5) # wait for the skip ad button to show up
            try:
                skip_ad_button = self.driver.find_element(By.CLASS_NAME, 'ytp-ad-skip-button-text')
                skip_ad_button.click()
                return
            except Exception as e:
                error('Cant skip')
                pass

            try:
                skip_ad_button = self.driver.find_element(By.CLASS_NAME, 'ytp-ad-skip-button-container')
                skip_ad_button.click()
                return
            except Exception as e:
                error('Cant skip')
                pass

    def chromeLogin(self):
        self.turnOnHistory()
        pass

    def convertToSource(self, source, origin):
        obj = {
            'id': source['id'],
            'platform': "youtube",
            'origin': origin,
            'position': source.get('position', None),
            'type': source['type'],
            'name': source.get('name', None),
            'secondary_source': source.get('secondary_source', None),
            'followers': source.get('subscribers', None),
            'description': source.get('description', None),
            'engagement': source.get('engagement', None),
            'url': source['urlId'],
        }
        return obj