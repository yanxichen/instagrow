import requests
import random
import re
from scipy import linalg, mat, dot
import numpy as np
import json
import csv
import time
from .constants import *
from .pageparser import PageParser
# from tagdict import TagDict
import os


class InstaGrow:

    def __init__(self,
                 user,
                 password,
                 like_count):
        self.user = user
        self.password = password
        self.like_count = like_count
        self.user_agent = HEADERS_LIST[random.randrange(0, 4)]
        self.accept_language = 'en-US,en;q=0.9'
        dirname = os.path.dirname(__file__)
        self.follow_list_file = os.path.join(dirname, 'follow_list.csv')
        self.black_list_file = os.path.join(dirname, 'black_list.csv')
        self.unfollow_list_file = os.path.join(dirname, 'unfollow_list.csv')
        self.session = requests.Session()
        self.logged_in = False
        self.session.get(BASE_URL)
        self.csrftoken = self.session.cookies['csrftoken']
        self.login()
        self.liked_list_current = []
        self.unfollow_count = 0

    def login(self):
        self.session.headers.update({
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            # 'Host': 'www.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Referer': BASE_URL,
            'X-Instagram-AJAX': '1ea1c140d95d',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'user-agent': self.user_agent
                                     })
        r = self.session.get(BASE_URL)
        csrftoken = re.search('(?<=\"csrf_token\":\")\w+', r.text).group(0)
        self.session.headers.update({'X-CSRFToken': csrftoken})
        login_data = dict(username=self.user, password=self.password, allow_redirects=True)
        login = self.session.post(LOGIN_URL, data=login_data, headers={'Referer': 'https://www.instagram.com/'})
        self.session.headers.update({'X-CSRFToken': csrftoken})
        # print(login.cookies['csrftoken'])
        page = self.session.get(BASE_URL)
        if login.status_code == 200:
            if page.text.find('not-logged-in') == -1:
                print("login success")
                self.logged_in = True
            else:
                print(page.content)
                print("login error")
        else:
            print("connection failure")

    def hashtag_campaign(self):
        for hashtag in HASHTAGS:
            hashtag_url = HASHTAG_URL % hashtag
            posts = PageParser(self.session, hashtag_url).parse_hashtag_page()
            for c, post in enumerate(posts):
                if c == SAMPLE_SIZE:
                    break
                if MIN_LIKES < post['like_count'] < MAX_LIKES:
                    print('To like ' + post['shortcode'])
                    self.like_id(post['media_id'])

                    post_url = POST_URL % post['shortcode']
                    try:
                        post_parser = PageParser(self.session, post_url).parse_post_page()
                        owner_username = post_parser['owner_username']

                        user_url = USER_URL % owner_username
                        user = PageParser(self.session, user_url).parse_user_page()

                        if user['follower_count'] < MAX_FOLLOWER_COUNT:
                            print('To like photos from ' + owner_username)
                            self.like_on_user(user, 3)

                            user_hashtags = self.get_hashtag_from_user(user)
                            similarity = self.similarity(user_hashtags, HASHTAGS)

                            if similarity > MIN_SIMILARITY and not user['followed_by_viewer']:
                                self.follow(user['user_id'])
                                print('followed ' + owner_username)
                                self.add_to_follow_list(owner_username, user['follows_viewer'], time.time(),
                                                        user['user_id'])

                    except KeyError:
                        print("cannot access post: " + post_url)

                    except AttributeError:
                        print("connection error: " + post_url)

    def maintain_following_user(self):

        with open(self.follow_list_file, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            rows = list(reader)
        for row in rows:
            username = row[0]
            user_url = USER_URL % username
            user_parser = PageParser(self.session, user_url).parse_user_page()
            try:
                if not user_parser['followed_by_viewer']:
                    rows.remove(row)
                    self.add_to_blacklist(username)
                    print("not following " + username + " anymore, added to blacklist")
                    continue
                if not user_parser['follows_viewer']:
                    if (time.time() - float(row[2])) > 24 * 60 * 60 * NUM_OF_DAYS_TO_FOLLOW:
                        print('to unfollow ' + username)
                        self.unfollow(user_parser['user_id'], 1)
                        rows.remove(row)
                        self.add_to_blacklist(username)
                        time.sleep(60)
                        continue

                else:
                    # print(username + ' is following you now!')
                    row[1] = True
                # print('Liking ' + username + '\'s photos now')
                self.like_on_user(user_parser, 3)
            except TypeError:
                print('cannot parse page: ' + user_url)
                print('to unfollow ' + username)
                self.unfollow(row[3], 1)
                rows.remove(row)
                time.sleep(60)

        with open(self.follow_list_file, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')
            writer.writerows(rows)

    def like_on_user(self, parsed_user, num_to_like):
        # media_id_list = []
        # for c, post in enumerate(parsed_user['posts']):
        #     if c == SAMPLE_SIZE:
        #         break
        #     media_id_list.append(post['media_id'])
        #
        # to_like_list = random.choices(population=media_id_list, k=num_to_like)
        # self.like(to_like_list)
        # print('Liking ' + to_like_list)

        # for debugging
        media_id_list = []
        for c, post in enumerate(parsed_user['posts']):
            if c == SAMPLE_SIZE:
                break
            media_id_list.append({post['media_id']: post['shortcode']})
        min_num_to_like = min(num_to_like, len(media_id_list))
        try:
            to_like_list = random.sample(population=media_id_list, k=min_num_to_like)
            # print('to like the following:')
            # print(to_like_list)

            to_like_id = []
            for post in to_like_list:
                for post_id in post.keys():
                    to_like_id.append(post_id)
            self.like(to_like_id)
        except IndexError:
            print('User has no posts')

    def get_hashtag_from_user(self, parsed_user):
        hashtags = []
        for post in parsed_user['posts']:
            for hashtag in post['hashtags']:
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        return hashtags

    def get_media_id(self, post_url):
        post = self.session.get(post_url)
        text = post.text
        media_id = re.search('media\?id=([0-9]+)', text).group(1)
        if media_id:
            return media_id

    def like(self, media_id_list):
        for media_id in media_id_list:
            self.like_id(media_id)

    def like_id(self, media_id):
        if media_id in self.liked_list_current:
            print('Already liked ' + media_id)
        elif media_id not in self.liked_list_current:
            like_url = LIKE_URL % media_id
            self.session.post(like_url)
            self.like_count += 1
            self.liked_list_current.append(media_id)

    def follow(self, user_id):
        if self.logged_in:
            follow_url = FOLLOW_URL % user_id
            self.session.post(follow_url)

    def unfollow(self, user_id, num_of_tries):
        if self.logged_in:
            unfollow_url = UNFOLLOW_URL % user_id
            unfo = self.session.post(unfollow_url)
            if unfo.status_code != 200:
                if num_of_tries <= 3:
                    print('Error: cannot unfollow user, trying again in 2 minutes')
                    num_of_tries += 1
                    time.sleep(120)
                    self.unfollow(user_id, num_of_tries)
                else:
                    print('Error: cannot unfollow user, maximum tries reached. Added to unfollow list')
                    self.add_to_unfollowlist(user_id)

    def add_to_follow_list(self, username, following_viewer, timestamp, user_id):
        # TODO column 0 - username; column 1 - if follows viewer; column 2 - current time stamp

        if not os.path.isfile(self.follow_list_file):
            with open(self.follow_list_file, 'w') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
                filewriter.writerow([username, following_viewer, timestamp, user_id])
        else:
            with open(self.follow_list_file, 'a') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
                filewriter.writerow([username, following_viewer, timestamp, user_id])

    def delete_from_follow_list(self, username, follow_list):
        for row in follow_list:
            if row[0] == username:
                follow_list.remove(row)

    def add_to_blacklist(self, username):
        if not os.path.isfile(self.black_list_file):
            with open(self.black_list_file, 'w') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
                filewriter.writerow([username])
        else:
            with open(self.black_list_file, 'a') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
                filewriter.writerow([username])

    def add_to_unfollowlist(self, userid):
        if not os.path.isfile(self.unfollow_list_file):
            with open(self.unfollow_list_file, 'w') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
                filewriter.writerow([userid])
        else:
            with open(self.unfollow_list_file, 'a') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
                filewriter.writerow([userid])

    def similarity(self, tag_list1, tag_list2):
        all_tags = tag_list1.copy()
        for tag in tag_list2:
            if tag not in all_tags:
                all_tags.append(tag)
        matrix1 = []

        for tag in all_tags:
            if tag in tag_list1:
                matrix1.append(1)
            else:
                matrix1.append(0)

        matrix2 = []

        for tag in all_tags:
            if tag in tag_list2:
                matrix2.append(1)
            else:
                matrix2.append(0)

        matrix = mat([matrix1, matrix2])

        similarity = dot(matrix[0], matrix[1].T) / np.linalg.norm(matrix[0]) / np.linalg.norm(matrix[1])
        return similarity
