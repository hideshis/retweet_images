from config import default
from package.twitterapi import twitter_api
import datetime

# フォローしているアカウントのIDリストを取得する
def get_friend_screen_name_list():
    twitter = twitter_api.TwitterApi()
    screen_name_list = twitter.get_friend_screen_name_list()
    position = get_position()
    return split_list(screen_name_list, 4)[position] # IDリストを4分割する。また、スクリプト実行時の時間に応じて、分割したリストのうちどの部分リストを対象とするか決定する

def get_position():
    position = -1
    t_now = str(datetime.datetime.now().time())[:2]
    if t_now == "5":
        position = 0
    elif t_now == "11":
        position = 1
    elif t_now == "18":
        position = "2"
    elif t_now == "21":
        position = 3
    return position

'''
リストlistをn等分する
実行例：
>>> a = range(16)
>>> split_list(a,5)
[[0, 1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]
docs: http://muscle199x.blog.fc2.com/blog-entry-70.html
'''
def split_list (list,n):
    list_size = len(list)
    a = list_size // n # aは、list_sizeをnで割った時の商
    b = list_size % n # bは、list_sizeをnで割った時の剰余
    return [list[i*a + (i if i < b else b):(i+1)*a + (i+1 if i < b else b)] for i in range(n)]

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
