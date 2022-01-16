from config import default
from package.twitterapi import twitter_api


# フォローしているアカウントのIDリストを取得する
def get_friend_screen_name_list():
    twitter = twitter_api.TwitterApi()
    screen_name_list = twitter.get_friend_screen_name_list()
    return screen_name_list


# リツイート対象のツイートIDリストを取得する
def get_target_tweet_id_list(screen_name):
    twitter = twitter_api.TwitterApi()
    retweet_target_id_list = twitter.recent_search(screen_name)
    return retweet_target_id_list


# ツイートをリツイートする
def retweet_tweet(tweet_id):
    twitter = twitter_api.TwitterApi()
    retweet_result = twitter.retweet(tweet_id)
    return retweet_result


# 最新1500件分の、リツイートしたツイートのIDを取得する
def get_retweeted_tweet_id_list():
    retweeted_tweet_id_list = []
    twitter = twitter_api.TwitterApi()
    user_id = default.USER_ID
    pagination_next_token = ''
    for i in range(0, 15):
        timeline_dict = twitter.get_tweet_timeline(user_id, pagination_next_token)
        pagination_next_token = timeline_dict['pagination_next_token']
        retweeted_tweet_id_list.extend(timeline_dict['retweeted_tweet_id_list'])
    return retweeted_tweet_id_list


def lambda_handler(event, context):
    retweeted_tweet_id_list = get_retweeted_tweet_id_list()
    print(retweeted_tweet_id_list)

    tweets_hit_by_search_count = 0
    tweets_successfully_retweeted_count = 0
    tweets_unsuccessfully_retweeted_count = 0
    screen_name_list = get_friend_screen_name_list()
    for screen_name in screen_name_list:
        print(screen_name)
        tweet_id_list = get_target_tweet_id_list(screen_name)
        tweets_hit_by_search_count += len(tweet_id_list)
        for tweet_id in tweet_id_list:
            if tweet_id in retweeted_tweet_id_list:
                continue
            else:
                if retweet_tweet(tweet_id):
                    tweets_successfully_retweeted_count += 1
                else:
                    tweets_unsuccessfully_retweeted_count += 1

        print(tweet_id_list)
        print("===")

    print("***summary***")
    print("list of your friend(following accounts): " + str(screen_name_list))
    print("# of your friend(following accounts): " + str(len(screen_name_list)))
    print("# of tweets hit by tweet search: " + str(tweets_hit_by_search_count))
    print("# of tweets successfully retweeted: " + str(tweets_successfully_retweeted_count))
    print("# of tweets unsuccessfully retweeted: " + str(tweets_unsuccessfully_retweeted_count))

if __name__ == "__main__":
    lambda_handler(None, None)
