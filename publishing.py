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
from utils import retrieve_token, retrieve_current_time_scheduled_posts
import facebook
from CONST import twitter_api_key, twitter_api_secret, linkedin_client_id, linkedin_client_secret, facebook_client_id, facebook_client_secret

"""
# postgresql details
sql_dbname = "postgres"
sql_pass = "brasql20"
sql_host = "pdb"
sql_user = "postgres"
sql_port = "5432"

conn = psycopg2.connect(dbname=sql_dbname, user=sql_user, password=sql_pass, host=sql_host, port=sql_port)


with conn:
    # to enable creating statements
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur: # with the dictcursor, you can return select cell of a row, by mentioning the column name like a dictionary

        # to execute a statement
        cur.execute("DROP TABLE IF EXISTS customers CASCADE;")
        cur.execute("DROP TABLE IF EXISTS products CASCADE;")
        cur.execute("DROP TABLE IF EXISTS trans_id CASCADE;")
        cur.execute("DROP TABLE IF EXISTS transactions CASCADE;")
        cur.execute("DROP TABLE IF EXISTS tokens CASCADE;")
        cur.execute("DROP TABLE IF EXISTS requests CASCADE;")
        cur.execute("DROP TABLE IF EXISTS analytis_publishing CASCADE;")
        cur.execute("DROP TABLE IF EXISTS analytics_listening CASCADE;")
        cur.execute("DROP TABLE IF EXISTS trans_id CASCADE;")

        # to execute a statement
        cur.execute("CREATE TABLE customers (customer_id serial PRIMARY KEY, handler_name VARCHAR (50), job_title VARCHAR (100), company_name VARCHAR (100), username VARCHAR (50), password VARCHAR (200), country VARCHAR (50), state VARCHAR (50), industry VARCHAR (100), current_plan VARCHAR (50), signup_time VARCHAR (50), email VARCHAR (100), last_signedin VARCHAR (50));")
        cur.execute("CREATE TABLE products (product_id serial PRIMARY KEY, product_name VARCHAR (50), unit_price FLOAT (3), created_datastamp VARCHAR (50), status VARCHAR (20));")
        cur.execute("CREATE TABLE transactions (trans_id serial PRIMARY KEY, product_id INT REFERENCES products (product_id), customer_id INT REFERENCES customers (customer_id), unit_bought INT, amount_paid FLOAT (3), transaction_datestamp VARCHAR (50), payment_solution VARCHAR (100), order_status VARCHAR (50));")
        cur.execute("CREATE TABLE tokens (token_id serial PRIMARY KEY, customer_id INT REFERENCES customers (customer_id), token_key VARCHAR (200), social_media VARCHAR (50), sm_username VARCHAR (100), created_datestamp VARCHAR (50), status VARCHAR (50));")
        cur.execute("CREATE TABLE requests (request_id serial PRIMARY KEY, customer_id INT REFERENCES customers (customer_id), token_id INT REFERENCES tokens (token_id), request_category VARCHAR (50), request_datestamp VARCHAR (50));")
        cur.execute("CREATE TABLE analytis_publishing (pub_id serial PRIMARY KEY, post_id VARCHAR (100), customer_id INT REFERENCES customers (customer_id), num_likes INT, num_comments INT, num_shared INT, social_media VARCHAR (50), author_followers INT, sentiment VARCHAR (20));")
        cur.execute("CREATE TABLE analytics_listening (list_id serial PRIMARY KEY, mention_id VARCHAR (100), customer_id INT REFERENCES customers (customer_id), author_username VARCHAR (100), num_followers INT, date_created VARCHAR (50), social_media VARCHAR (100), sentiment VARCHAR(20));")

conn.close()
"""
"""
 # retrieve api keys and api secret
with open("api_keys.txt", "r") as file:
    twitter_api_key, twitter_api_secret, linkedin_client_id, linkedin_client_secret, facebook_client_id, facebook_client_secret = file.readlines()
"""
callback_uri = "oob" #"http://b6982216df7a.ngrok.io"
auth = tweepy.OAuthHandler(twitter_api_key[0:25], twitter_api_secret[0:50])

mongo_client = MongoClient("mongodb://mdb:27017")

# create a new mongo database using pymongo
mongo_db = mongo_client.bradb
publishing_collection = mongo_db["publishing"]
customers_collection = mongo_db["customers"]
listening_collection = mongo_db["listening"]


class Scheduling:
    def _init_(self):
        self._schedule = []

    # schedule post
    def schedule_post(self, email, password, post_datetime, media_type, media_username, message_text):
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

        # save message_text into publishing collection
        post_details = {"body": message_text,
        "email": email,
        "media_username": media_username,
        "media_type": media_type,
        "sm_profile_id": account_details[0][4],
        "token_key": account_details[0][2],
        "token_secret": account_details[0][3],
        "post_datetime": post_datetime,
        "post_type": "scheduled"
        }
        publishing_collection.insert_one(post_details)

        return "Your post has been scheduled for {}".format(post_datetime), 200

    # method to see all scheduled post
    def see_schedule(self, email, password):
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

        # confirm user has access to account, and find posts with the email = email provided in params
        all_posts = publishing_collection.find({"email": email})
        scheduled_posts = [(i["_id"], i["body"], i["media_username"], i["post_datetime"])
        for i in all_posts if i["post_type"]=="scheduled"]

        return scheduled_posts, 200

    # delete scheduled post method
    def kill_scheduled_post(self, email, password, post_id):
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

        # verify if user has access to the post
        correct_email = entry.verify_email_to_post(post_id, email)
        if not correct_email:
            return "Unauthorized request", 403

        # find the post to be deleted
        post_to_delete = publishing_collection.find_one({"_id": post_id})

        # delete the scheduled post
        publishing_collection.delete_one(post_to_delete)

        return "Post deleted", 200

    # change scheduled post method
    def change_schedule(self, email, password, post_id, new_message_text, post_datetime):
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

        # verify if user has access to the post
        correct_email = entry.verify_email_to_post(post_id, email)
        if not correct_email:
            return "Unauthorized request", 403

        # find the post to be deleted
        post_to_change = publishing_collection.find_one({"_id": post_id})

        # delete the scheduled post
        publishing_collection.update_one({
        "_id": post_id
        }, {
        "$set": {
        "body": new_message_text,
        "post_datetime": post_datetime
        }
        })

        return "Post updated", 200

    # get published posts for Twitter
    def get_posts_twitter(self, email, password, media_username, media_type="twitter"):
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
        # confirm user has access to account, and also retrieve the right token key and secret
        account_details = retrieve_token(email)

        # fetch requested data
        if media_type == media_type:
            try:
                # authenticate twitter app with user account
                auth.set_access_token(account_details[0][2], account_details[0][3])
                api = tweepy.API(auth, wait_on_rate_limit=True)
                api.verify_credentials()
                print("Authentication OK")
            except:
                return "Error during authentication"

            finally:
                # Retrieve users recent tweets on Twitter
                user_all_tweets_details = api.user_timeline(screen_name = account_details[0][1], count = 15, include_rts = False)
                # Collect required details only
                user_tweets_details = [(status.text, status.user.screen_name, status.favorite_count, status.retweet_count) for status in my_tweets]
                return user_tweets_details, 200

    # get published posts for LinkedIn
    def get_posts_linkedin(self, email, password, media_username, media_type="linkedin"):
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
        # confirm user has access to account, and also retrieve the right token key and secret
        account_details = retrieve_token(email)

        if media_type == media_type:
            # linkedin url for retrieving posts
            url = "https://api.linkedin.com/v2/ugcPosts?q=authors&authors=List(urn%3Ali%3Aorganization%3A{})&sortBy=LAST_MODIFIED".format(sm_profile_id)
            # required parameter
            params = {'oauth2_access_token': token_key}
            # retrieve posts
            response = requests.get(url, params=params)
            # loop through posts
        return response # to change it when Linkedin solve issue

    # To publish Twitter scheduled post
    def twitter_schedule_publish(self, email, password, media_username, post_datetime, media_type="twitter"):
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

        # confirm user has access to account, and find posts with the email = email provided in params
        current_time_scheduled_posts = retrieve_current_time_scheduled_posts(email)
        
        # loop through current_time_scheduled_posts to publish content to appropriate media platform
        for post in current_time_scheduled_posts:
            # post right content to Twitter
            if post[3] == media_type:
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
                    api.update_status(post[1])
        return "Post successfully published to Twitter", 200

    # To publish LinkedIn scheduled post
    def linkedin_schedule_publish(self, email, password, media_username, post_datetime, media_type="linkedin"):
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

        # confirm user has access to account, and find posts with the email = email provided in params
        current_time_scheduled_posts = retrieve_current_time_scheduled_posts(email)

        # loop through current_time_scheduled_posts to publish content to appropriate media platform
        for post in current_time_scheduled_posts:
            # post right content to Twitter
            if post[3] == media_type:
                # linkedin api url for posting
                url = "https://api.linkedin.com/v2/ugcPosts"
                # header parameter
                headers = {'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0',
                'Authorization': 'Bearer ' + post[5]}
                # post json
                post_data = {
                    "author": "urn:li:organization:"+post[4],
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": post[1]
                                },
                                "shareMediaCategory": "NONE"
                                }
                                },
                                "visibility": {
                                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                                    }
                                    }
                # try posting content
                try:
                    requests.post(url, headers=headers, json=post_data)
                except:
                    print("Error trying to post content")
        return "Post successfully published to LinkedIn", 200

    # To publish Facebook scheduled post
    def facebook_schedule_publish(self, email, password, media_username, post_datetime, media_type="facebook"):
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

        # confirm user has access to account, and find posts with the email = email provided in params
        current_time_scheduled_posts = retrieve_current_time_scheduled_posts(email)

        # loop through current_time_scheduled_posts to publish content to appropriate media platform
        for post in current_time_scheduled_posts:
            # post right content to Twitter
            if post[3] == media_type:
                # connect facebook app to the access token for the user
                graph = facebook.GraphAPI(post[5])
                # retrieve all the pages associate to the user - "me"
                accounts = graph.get_connections(id="me", connection_name="accounts")
                # iterates through all the pages to get the very page id number user want to post to
                for page in accounts["data"]:
                    if page["name"] == post[2]:
                        identity_number = page["id"]
                        token_key = page["access_token"]
                # connect facebook app to the access token for that very page
                graph_page = facebook.GraphAPI(token_key)
                # post scheduled text to facebook
                graph_page.put_object(parent_object=identity_number, connection_name="feed", message=post[1])

        return "Post successfully published to LinkedIn", 200





# for quick publishing to social media
class QuickPost:
    def _init_(self):
        self._quick_post = []
    
    # To make quick post to Twitter
    def twitter_quick_post(self, email, password, media_username, message_text, media_type="twitter"):
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

        # save message_text into publishing collection
        post_details = {"body": message_text,
        "email": email,
        "media_username": media_username,
        "media_type": media_type,
        "token_key": account_details[0][2],
        "token_secret": account_details[0][3],
        "post_datetime": post_datetime,
        "post_type": "quick"
        }
        publishing_collection.insert_one(post_details)

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
            api.update_status(message_text)
        return "Post successfully published to Twitter", 200

    
    # To make quick post to LinkedIn
    def linkedin_quick_post(self, email, password, media_username, message_text, media_type="linkedin"):
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

        # save message_text into publishing collection
        post_details = {"body": message_text,
        "email": email,
        "media_username": media_username,
        "media_type": media_type,
        "sm_profile_id": account_details[0][4],
        "token_key": account_details[0][2],
        "post_datetime": post_datetime,
        "post_type": "quick"
        }
        publishing_collection.insert_one(post_details)

        # linkedin api url for posting
        url = "https://api.linkedin.com/v2/ugcPosts"
        # header parameter
        headers = {'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
        'Authorization': 'Bearer ' + token_key}
        # post json
        post_data = {
            "author": "urn:li:organization:"+sm_profile_id,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": message_text
                        },
                        "shareMediaCategory": "NONE"
                        }
                        },
                        "visibility": {
                            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                            }
                            }
        # try posting content
        try:
            requests.post(url, headers=headers, json=post_data)
        except:
            print("Error trying to post content")
        return "Post successfully published to LinkedIn", 200