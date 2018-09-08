import os
import csv

BASE_URL = 'https://www.instagram.com/'
LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
HEADERS_LIST = [
        "Mozilla/5.0 (Windows NT 5.1; rv:41.0) Gecko/20100101"
        " Firefox/41.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2)"
        " AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2"
        " Safari/601.3.9",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0)"
        " Gecko/20100101 Firefox/15.0.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
        " Edge/12.246"
        ]

LIKE_URL = 'https://www.instagram.com/web/likes/%s/like/'
UNLIKE_URL = 'https://www.instagram.com/web/likes/%s/unlike/'
HASHTAG_URL = 'https://www.instagram.com/explore/tags/%s/'
USER_URL = 'https://www.instagram.com/%s/'
POST_URL = 'https://www.instagram.com/p/%s/'
UNFOLLOW_URL = 'https://www.instagram.com/web/friendships/%s/unfollow/'
FOLLOW_URL = 'https://www.instagram.com/web/friendships/%s/follow/'
HASHTAGS = ['foodie', 'bookworm', 'ootd', 'fashionblogger', 'banff', 'EarthVisuals', 'portrait', 'instagood',
            'artofvisuals', 'naturelovers', 'liveauthentic', 'yycliving', 'yycphotographer', 'travel', 'mothernature',
            'instatravel', 'beautifuldestinations', 'travelstoke', 'ExploreCanada', 'letsgosomewhere', 'agameoftones',
            'sheisnotlost']


def find_preset(parameter):
        dirname = os.path.dirname(__file__)
        preset_file = os.path.join(dirname, 'preset.csv')

        with open(preset_file, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                rows = list(reader)
                for row in rows:
                        if row[0] == parameter:
                                return row[1]


MIN_LIKES = int(find_preset('min_likes'))
MAX_LIKES = int(find_preset('max_likes'))
MIN_FOLLOWER_FOLLOWING_RATIO = 0.6
MAX_FOLLOWER_FOLLOWING_RATIO = 2
MAX_FOLLOWER_COUNT = int(find_preset('max_follower_count'))
MIN_SIMILARITY = float(find_preset('min_similarity'))
SAMPLE_SIZE = 10
NUM_OF_DAYS_TO_FOLLOW = int(find_preset('num_of_days_to_follow'))
MAX_DAILY_LIKES = int(find_preset('max_daily_likes'))

