# -*- coding: utf-8 -*-

# source: https://github.com/twitterdev/Twitter-API-v2-sample-code
# source: https://github.com/pigeonburger/twitter-api-v2-python

import requests
import os
import json
import datetime
import sys
from requests_oauthlib import OAuth1, OAuth1Session
from ui import Colors as colors

#You will need to have Python 3 installed to run this code. The Python samples use requests==2.24.0 which uses requests-oauthlib==1.3.0.
#You can install these packages as follows:
#pip install requests
#pip install requests-oauthlib

class Tbot:

    oauth = None
    oauthSession = None
    oauth_tokens = None
    access_token_secret = None

    client_key = ""
    client_secret = ""
    access_token = ""
    access_token_secret = ""
    bearer_token = ""
    
    session_opened = False
            
    def __open_session(self):
        self.session_opened = False
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"

        self.oauthSession = OAuth1Session(self.client_key, client_secret=self.client_secret)

        try:
            fetch_response = self.oauthSession.fetch_request_token(request_token_url)
        except ValueError:
            colors.error("Error: There may have been an issue with the consumer_key or consumer_secret in config file.")
            sys.exit()

        try:
            resource_owner_key = fetch_response.get("oauth_token")
            resource_owner_secret = fetch_response.get("oauth_token_secret")
            colors.info(f"Info: Got OAuth token: {resource_owner_key}")
        except:
            colors.error("Error: Not able to receive OAuth token")
            sys.exit()

        try:
            base_authorization_url = "https://api.twitter.com/oauth/authorize"
            authorization_url = self.oauthSession.authorization_url(base_authorization_url)
            print(f"Please go here and authorize: {authorization_url}")
            verifier = input("Paste the PIN here: ")

            access_token_url = "https://api.twitter.com/oauth/access_token"
            self.oauthSession = OAuth1Session(
                client_key = self.client_key,
                client_secret = self.client_secret,
                resource_owner_key = resource_owner_key,
                resource_owner_secret = resource_owner_secret,
                verifier = verifier,
            )
            self.oauthSession_tokens = self.oauthSession.fetch_access_token(access_token_url)

        except:
            colors.error("Error: Failed to authorise app.")
            sys.exit()

        try:
            self.access_token = self.oauthSession_tokens["oauth_token"]
            self.access_token_secret = self.oauthSession_tokens["oauth_token_secret"]

            self.oauthSession = OAuth1Session(
                client_key = self.client_key,
                client_secret = self.client_secret,
                resource_owner_key = self.access_token,
                resource_owner_secret = self.access_token_secret,
            )
        except Exception as e:
            colors.error("Error: Not able to open session.")
            sys.exit()

        self.session_opened = True
        colors.info("Info: Session opened.")


    def create_tweet(self, text: str):

        if self.session_opened == False:
            colors.warn("Warning: Session is closed.")
            colors.info("Info: Trying to reopen the session.")
            self.__open_session()

            if self.session_opened == False:
                colors.error("Error: Cannot reopen the session. Exiting...")
                sys.exit()

        payload = {"text": text}

        try:
            response = self.oauthSession.post("https://api.twitter.com/2/tweets", json = payload)
        except Exception as e:
            colors.warn("Warning: Not able to post a tweet. Skipping...")
            return

        if response.status_code != 201:
            colors.warn(f"Warning: Request returned an error: {response.status_code}\n{response.text}")
            return

        colors.info(f"Info: Tweet created.")


    def reply_on_tweet(self, text: str, tweet_id: str):

        if self.session_opened == False:
            colors.warn("Warning: Session is closed.")
            colors.info("Info: Trying to reopen the session.")
            self.__open_session()

            if self.session_opened == False:
                colors.error("Error: Cannot reopen the session. Exiting...")
                sys.exit()

        payload = {
            "text": text, 
            "reply": 
            { 
                "in_reply_to_tweet_id": tweet_id
            }}

        try:
            response = self.oauthSession.post("https://api.twitter.com/2/tweets", json = payload)
        except Exception as e:
            colors.warn("Warning: Not able to post a tweet. Skipping...")
            return

        if response.status_code != 201:
            colors.warn(f"Warning: Request returned an error: {response.status_code}\n{response.text}")
            return

        colors.info(f"Info: Tweet created.")
        

    def get_recent_tweets_for_user(self, user: str, max_results = 10):
        url = "https://api.twitter.com/2/tweets/search/recent"
        fields = "author_id"
        query_params = {'query': f'from:{user}', 'max_results': max_results, 'tweet.fields': fields}
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        r = requests.get(url, headers=headers, params=query_params)
        return r.json()


    def get_user_id(self, users) -> str:
        users = ",".join(users)
        url = "https://api.twitter.com/2/users/by"
        query_params = {
            "usernames": users, 
            "user.fields": "created_at,description,id"
            }
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        r = requests.get(url, headers=headers, params=query_params)

        if r.status_code != 200:
            colors.warn(f"Warning: Received status code {r.status_code}\n{r.text}")
            return None
        
        text = r.json()

        if text is None: return None
        else: 
            try:
                if len(text["data"]) == 0:
                    colors.warn(f"Warning: User not found.")
                    return None

                else:
                    l = []
                    for i in range(0, len(text["data"])):
                        l.extend([text["data"][i]["id"]])
                    return l
            except:
                colors.warn(f"Warning: Empty response received for user.")
                return None


    def get_last_tweet_id(self, user):
        url = "https://api.twitter.com/2/tweets/search/recent"
        query_params = {
            "query": f"from:{user}", 
            "max_results": 10,
            "tweet.fields": "id",
            "user.fields": "id"
            }
        headers = {"Authorization": f"Bearer {self.bearer_token}"}

        id = None
        try:
            r = requests.get(url, headers=headers, params=query_params)
            if r.status_code == 200:
                r = r.json()
                if r["meta"]["result_count"] > 0:
                    id = r["meta"]["newest_id"]
                else: return 0
            else:
                colors.warn(f"Warning: Got status code: {r.status_code} for user id {user}")
        except Exception as e:
            colors.error(f"Error: Could not retrieve last tweet id for {user}. Exiting...")
            sys.exit()
        return id

    def get_tweets_newer_than_id(self, user, tweet_id):

        if tweet_id == 0: return [], []
        
        url = "https://api.twitter.com/2/tweets/search/recent"
        query_params = {
            "query": f"from:{user}", 
            "since_id": tweet_id,
            "tweet.fields": "id,text"
            }
        headers = {"Authorization": f"Bearer {self.bearer_token}"}

        l = []
        t = []

        try:
            r = requests.get(url, headers=headers, params=query_params)
            r = r.json()

            if r["meta"]["result_count"] > 0:
                for i in range(0, len(r["data"])):
                    l.extend([r["data"][i]["id"]])
                    t.extend([r["data"][i]["text"]])

        except Exception as e:
            colors.error("Error: Could not retrieve last tweets. Exiting...")
            sys.exit()
        return l, t


    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, bearer_token):
        self.client_key = consumer_key
        self.client_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.bearer_token = bearer_token

        try:
            self.__open_session()
        except Exception as e:
            colors.error("Error: Unable to set OAuth1.")
            sys.exit()

        colors.warn("Warning: Tbot loaded.")
