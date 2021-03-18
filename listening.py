import requests
import bcrypt
import datetime
from pymongo import MongoClient
#import psycopg2
#import psycopg2.extras
import tweepy
from access import Entry
import json
import random
import string


 # retrieve api keys and api secret
with open("api_keys.txt", "r") as file:
    twitter_api_key, twitter_api_secret, linkedin_client_id, linkedin_client_secret, facebook_client_id, facebook_client_secret = file.readlines()

callback_uri = "oob" #"http://b6982216df7a.ngrok.io"
auth = tweepy.OAuthHandler(twitter_api_key[0:25], twitter_api_secret[0:50])

mongo_client = MongoClient("mongodb://mdb:27017")

# create a new mongo database using pymongo
mongo_db = mongo_client.bradb
publishing_collection = mongo_db["publishing"]
customers_collection = mongo_db["customers"]
listening_collection = mongo_db["listening"]


class AddKeyword:
    def _init_(self):
        self._keyword = []
    
    # To Collect and save keywords from users for listening on Twitter
    def add_keyword_twitter(self, email, password, keyword, media_username, media_type="twitter"):
        # confirm if email is in database
        try:
            customers_collection.find_one({"email": email})
        except:
            return "Email does not exist", 402
        # confirm email-password match
        entry = Entry()
        correct_password = entry.verify_password(email, password)
        if not correct_password:
            return "Incorrect password", 405

        # confirm user has access to account, and also retrieve the token key and secret
        account_details = retrieve_token(email)

        # save contents to listening colletion
        keyword_details = {"email": email,
        "media_username": media_username,
        "media_type": media_type,
        "token_key": account_details[0][2],
        "token_secret": account_details[0][3],
        "keyword": keyword
        }
        listening_collection.insert_one(keyword_details)

        return "{} has been added successfully".format(keyword), 200

    # To Collect and save keywords from users for listening on LinkedIn
    def add_keyword_linkedin(self, email, password, keyword, media_username, media_type="linkedin"):
        # confirm if email is in database
        try:
            customers_collection.find_one({"email": email})
        except:
            return "Email does not exist", 402
        # confirm email-password match
        entry = Entry()
        correct_password = entry.verify_password(email, password)
        if not correct_password:
            return "Incorrect password", 405

        # confirm user has access to account, and also retrieve the token key and secret
        account_details = retrieve_token(email)

        # save contents to listening colletion
        keyword_details = {"email": email,
        "media_username": media_username,
        "media_type": media_type,
        "sm_profile_id": account_details[0][4],
        "token_key": account_details[0][2],
        "keyword": keyword
        }
        listening_collection.insert_one(keyword_details)

        return "{} has been added successfully".format(keyword), 200


class Listening:
    def _init_(self):
        self._listen = []
    
    def twitter_listening(self, email, password, keyword, media_username, date_since, media_type="twitter"):
        # confirm if email is in database
        try:
            customers_collection.find_one({"email": email})
        except:
            return "Email does not exist", 402
        # confirm email-password match
        entry = Entry()
        correct_password = entry.verify_password(email, password)
        if not correct_password:
            return "Incorrect password", 405

        try:
            # authenticate twitter app with user account
            auth.set_access_token(token_key, token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            api.verify_credentials()
            print("Authentication OK")
        except:
            print("Error during authentication")
        finally:
            # Post Tweet on Twitter
            tweets = tweepy.Cursor(api.search, q = search_words, lang = "en",
                                since = date_since).items(10000)
        
        