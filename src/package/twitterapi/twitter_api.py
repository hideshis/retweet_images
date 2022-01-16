from config import default
from requests_oauthlib import OAuth1Session  # OAuthのライブラリの読み込み
import requests


class TwitterApi():
    def __init__(self) -> None:
        self.oauth_dict = self.get_authentications()
        self.bearer_token = self.oauth_dict["bearer_token"]
        self.oauth1 = self.oauth_dict["oauth1"]

    def get_tweet_timeline(self, user_id, pagination_next_token):
        # ref: http://benalexkeen.com/interacting-with-the-twitter-api-using-python/
        # ref: https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline.html
        url = "https://api.twitter.com/2/users/" + user_id + "/tweets" # タイムライン取得エンドポイント
        headers = {
            "Authorization": "Bearer {}".format(self.bearer_token),
        }
        params = {
                'max_results': 100,
                'tweet.fields': 'referenced_tweets'
        }
        if pagination_next_token != '':
            params['pagination_token'] = pagination_next_token
        result = requests.get(url, headers=headers, params=params)

        retweeted_tweet_id_list = []
        pagination_next_token = result.json()['meta']['next_token']
        for tweet in result.json()['data']:
            if ('referenced_tweets' in tweet) and (tweet['referenced_tweets'][0]['type'] == 'retweeted'):
                retweeted_tweet_id_list.append(tweet['referenced_tweets'][0]['id'])
        timeline_dict = {
            'retweeted_tweet_id_list': retweeted_tweet_id_list,
            'pagination_next_token': pagination_next_token
        }
        return timeline_dict

    def recent_search(self, screen_name):
        url = "https://api.twitter.com/2/tweets/search/recent"
        headers = {
            "Authorization": "Bearer {}".format(self.bearer_token),
        }
        parameter = {
            "query": "from:" + screen_name + " -is:retweet -is:reply -is:quote -has:mentions has:media has:images",
            "max_results": "100",
            "tweet.fields": "author_id,created_at,lang,source",
            "expansions": "attachments.poll_ids,attachments.media_keys,author_id",
            "media.fields": "duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics"
        }

        response = requests.get(url, headers=headers, params=parameter)
        response_json = response.json()

        retweet_target_id_list = []
        if response.status_code == 200 and "data" in response_json.keys():  # if response_json has results, i.e., target tweets, list becomes like: ['data', 'includes', 'meta']. Otherwise, it becomes like: ['meta']
            for value in response_json["data"]:
                retweet_target_id_list.append(value['id'])
        else:
            print(response.status_code, response_json, sep=", ")
        return retweet_target_id_list

    """
    retweetリクエストは、すでにリツイート済みのツイートに対して実行したとき327エラー(You have already retweeted this Tweet.)が返される。
    リツイート取り消し操作にはならない。
    """
    def retweet(self, tweet_id):
        url = "https://api.twitter.com/1.1/statuses/retweet/" + tweet_id + ".json"
        response = self.oauth1.post(url)
        response_json = response.json()

        if response.status_code == 200:
            print(tweet_id, response.status_code, "successfully retweeted", sep=", ")
            return True
        else:
            print(tweet_id, response.status_code, response_json, sep=", ")
            return False

    def user_lookup_by_username(self, user_name):
        url = "https://api.twitter.com/2/users/by/username/" + user_name
        headers = {
            "Authorization": "Bearer {}".format(self.bearer_token),
        }
        params = {
            'user.fields': 'description,entities,id,location,name,profile_image_url,url,username',
            'tweet.fields': 'author_id,entities,id'
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def tweet_lookup_single_tweet(self, tweet_id):
        url = "https://api.twitter.com/2/tweets/" + tweet_id
        headers = {
            "Authorization": "Bearer {}".format(self.bearer_token),
        }
        params = {
            'tweet.fields': 'attachments,author_id,created_at,entities,geo,id,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld',
            'expansions': 'attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id',
            'media.fields': 'duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics'            
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def get_friend_screen_name_list(self):
        url = "https://api.twitter.com/1.1/friends/list.json?count=200"
        response = self.oauth1.get(url)
        user_list = response.json()['users']
        screen_name_list = []
        for user in user_list:
            screen_name_list.append(user['screen_name'])
        return screen_name_list

    def get_authentications(self):
        CK = default.CONSUMER_KEY
        CS = default.CONSUMER_SECRET
        AT = default.ACCESS_TOKEN
        ATS = default.ACCESS_TOKEN_SECRET

        oauth_dict = {}
        oauth = self.get_oauth1(CK, CS, AT, ATS)
        bearer_token = self.get_bearer_token(CK, CS)
        oauth_dict["oauth1"] = oauth
        oauth_dict["bearer_token"] = bearer_token
        return oauth_dict

    def get_oauth1(self, CK, CS, AT, ATS):
        oauth1 = OAuth1Session(CK, CS, AT, ATS)
        return oauth1

    def get_bearer_token(self, CK, CS):
        # ref: https://developer.twitter.com/en/docs/basics/authentication/api-reference/token
        headers = { "Content-Type" : "application/x-www-form-urlencoded;charset=UTF-8"}
        data = { "grant_type":"client_credentials"}
        oauth2_url = "https://api.twitter.com/oauth2/token"
        response = requests.post(oauth2_url, data=data, headers=headers, auth=(CK, CS))
        bearer_token = response.json()["access_token"]
        return bearer_token

