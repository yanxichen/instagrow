import requests
import random
import re
import json
from .constants import *


class PageParser:

    def __init__(self, session, url):
        self.session = session
        self.url = url
        # test if url still works; sometimes user can delete post while script is running
        text = session.get(url).text
        try:
            self.script = json.loads(re.search('window\._sharedData = (.+);</script>', text).group(1))
        except KeyError:
            print('cannot access url: ' + url)
        except AttributeError:
            print('cannot parse page: ' + url)
        # print(self.script)
        # self.media_id_list = self.parse_hashtag_page(self.script, 'id')

    def parse_hashtag_page(self):
        # id, shortcode, edge_liked_by,
        try:
            text = self.script['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']
            count = text['count']
            i = min(count, SAMPLE_SIZE)
            posts = []

            for c, node in enumerate(text['edges'], 1):
                post = {'media_id': node['node']['id'],
                        'shortcode': node['node']['shortcode'],
                        'like_count': node['node']['edge_liked_by']['count'],
                        'owner_id': node['node']['owner']['id']
                        }
                posts.append(post)
                if c == i:
                    break
            return posts
        except KeyError:
            print('cannot parse page: ' + self.url)

    def parse_user_page(self):
        try:
            text = self.script['entry_data']['ProfilePage'][0]['graphql']['user']
            count = text['edge_owner_to_timeline_media']['count']
            i = min(count, SAMPLE_SIZE)
            posts = []
            user = {'follower_count': text['edge_followed_by']['count'],
                    'following_count': text['edge_follow']['count'],
                    'followed_by_viewer': text['followed_by_viewer'],
                    'follows_viewer': text['follows_viewer'],
                    'user_id': text['id'],
                    'posts': posts
                    }
            for c, node in enumerate(text['edge_owner_to_timeline_media']['edges'], 1):
                post = {'media_id': node['node']['id'],
                        'shortcode': node['node']['shortcode'],
                        'like_count': node['node']['edge_liked_by']['count'],
                        'hashtags': []
                        }
                caption_edge = node['node']['edge_media_to_caption']['edges']
                if len(caption_edge) > 0:
                    caption = caption_edge[0]['node']['text']
                    post['hashtags'] = self.get_hashtags_from_text(caption)

                if len(post['hashtags']) == 0:
                    post_url = POST_URL % post['shortcode']
                    post_parser = PageParser(self.session, post_url).parse_post_page()
                    post['hashtags'] = post_parser['hashtags']

                posts.append(post)
                if c == i:
                    break
            return user
        except (KeyError, AttributeError):
            print('Cannot parse page: ' + self.url)

    def parse_post_page(self):
        try:
            text = self.script['entry_data']['PostPage'][0]['graphql']['shortcode_media']
            comment_count = text['edge_media_to_comment']['count']
            like_count = text['edge_media_preview_like']['count']
            liked_by = []
            comments = []
            hashtags = []
            commenters = []
            comment_index = min(comment_count, SAMPLE_SIZE)
            like_index = min(like_count, SAMPLE_SIZE)
            post = {'owner_username': text['owner']['username'],
                    'shortcode': text['shortcode'],
                    'id': text['id'],
                    'viewer_has_liked': text['viewer_has_liked'],
                    'hashtags': hashtags,
                    'like_count': like_count,
                    'liked_by': liked_by,
                    'comment_count': comment_count,
                    'commenters': commenters
                    }

            caption_edge = text['edge_media_to_caption']['edges']

            for c, edge in enumerate(text['edge_media_to_comment']['edges']):
                if c == comment_index:
                    break

                if len(post['hashtags']) == 0:
                    comment_text = edge['node']['text']
                    post['hashtags'] = self.get_hashtags_from_text(comment_text)

                commenter = {
                    'id': edge['node']['owner']['id'],
                    'username': edge['node']['owner']['username']
                }
                commenters.append(commenter)

            for c, edge in enumerate(text['edge_media_preview_like']['edges']):
                if c == like_index:
                    break
                liked_user = edge['node']
                liked_by.append(liked_user)

            if len(caption_edge) > 0 and len(hashtags) == 0:
                caption = caption_edge[0]['node']['text']
                hashtags.append(self.get_hashtags_from_text(caption))

            return post
        except KeyError:
            print('cannot parse page: ' + self.url)

    def get_tags_from_hashtag_page(self):
        text = self.script['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']
        hashtags = []

        for edge in text['edges']:
            # print(edge)
            node = edge['node']['edge_media_to_caption']['edges']
            if len(node) > 0:
                comment = node[0]['node']['text']
                tags = re.findall('#([a-zA-Z]+)', comment)
                if len(tags) > 0:
                    hashtags.append(tags)

        return hashtags

    def get_hashtags_from_text(self, text):
        hashtags = re.findall('#([a-zA-Z]+)', text)
        return hashtags

