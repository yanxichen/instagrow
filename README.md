# InstaGrow

Grow your Instagram followers in an organic way by automating interactions with other users such as 
liking posts and following other users.

![](https://i.imgur.com/uhLFuks.gif)


## Features

- Elegant and intuitive command line interface
- Tested and proven algorithm that helps user gain 10 to 15 new followers every day
- Allows scheduled campaigns throughout the day
- Interacts with newly followed accounts on the user's behalf
- Easy to install and use

## Installation

Use `$ pip install .` to install the package and its dependencies. Run `instagrow` to start the script.


## Usage

### Settings:

```
MIN_LIKES               Min existing likes on a post
MAX_LIKES               Max existing likes on a post
MAX_FOLLOWER_COUNT      Max existing followers on an account
MIN_SIMILARITY          Min similarity between the user's and an account's hashtags
NUM_OF_DAYS_TO_FOLLOW   Max number of days to follow an account if not followed back
MAX_DAILY_LIKES         Max number of likes allowed in a day
```

### Hashtag Campaign

Likes posts under user-selected hashtags and follows accounts that use a similar set of hashtags
as the user.


### Follower Retention

Likes posts of accounts followed through InstaGrow. Unfollow accounts that have not followed back
after a user-defined number of days.

### Features Under Development

Influencer Campaign: interacts with accounts that have liked or commented on a post from user-selected
social influencers.

Location Campaign: interacts with accounts that have posted at user-selected locations.