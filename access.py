import bcrypt
import datetime
from pymongo import MongoClient
#import psycopg2
#import psycopg2.extras


mongo_client = MongoClient("mongodb://mdb:27017")

# create a new mongo database using pymongo
mongo_db = mongo_client.bradb
publishing_collection = mongo_db["publishing"]
customers_collection = mongo_db["customers"]
listening_collection = mongo_db["listening"]


class Entry:
    def _init_(self):
        self._entry = []

    # signup method
    def signup(self, fullname, email, password):
        # confirm email is valid

        # confirm if email has been signed up before

        # hash password
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        # collect time of signup
        signup_time = str(datetime.datetime.now())

        # create lastsigned time
        last_signedin_time = signup_time

        # generate username
        username = fullname.lower() # convert name to all lower case
        username = fullname.split(" ") # split each word into items of a list
        username = ".".join(username)

        # save data into mongo_db customers table
        #customers_collection = mongo_db["customers"]
        customer_details = {"handler_name": fullname,
        "email": email,
        "username": username,
        "password": hashed_pw,
        "signup_time": signup_time,
        "last_signedin": last_signedin_time
        }
        customers_collection.insert_one(customer_details)

        return "successfully signed up", 200

    # method to verify password before allowing login
    def verify_password(self, email, password):
        hashed_pw = customers_collection.find({"email":email})[0]["password"]

        if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
            return True
        else:
            return False

    # login method
    def login(self, email, password):
        # confirm if email is in database
        try:
            customers_collection.find_one({"email": email})
        except:
            return "Email does not exist", 402
        # confirm email-password match
        correct_password = self.verify_password(email, password)
        if not correct_password:
            return "Incorrect password", 405
        # grant access to platform

        # save required data to database
        last_signedin = str(datetime.datetime.now())

        customers_collection.update({"email": email},
        {"$set": {"last_signedin": last_signedin}})

        return "Welcome {}".format(email), 200

    # method to confirm if user has access to post
    def verify_email_to_post(post_id, email):
        post_details = publishing_collection.find_one({"_id": post_id})
        if post_details["email"] == email:
            return True
        else:
            return False

# Add account class
class AddAccount:
    def _init_(self):
        self._add_account = []

    # to Add Twitter tokens to database from the frontend
    def add_twitter(self, email, password, twitter_key, twitter_secret):
        try:
            customers_collection.find_one({"email": email})
        except:
            return "Email does not exist", 402
        # confirm email-password match
        entry = Entry()
        correct_password = entry.verify_password(email, password)
        if not correct_password:
            return "Incorrect password", 405
        
        # update user data with Twitter tokens
        customers_collection.update({"email": email},
        {"$set": {"twitter_token": [twitter_key, twitter_secret]}})

        return "Your Twitter profile has been successfully added", 200

    # to add LinkedIn tokens to database from the frontend
    def add_linkedin(self, email, password, linkedin_token):
        try:
            customers_collection.find_one({"email": email})
        except:
            return "Email does not exist", 402
        # confirm email-password match
        entry = Entry()
        correct_password = entry.verify_password(email, password)
        if not correct_password:
            return "Incorrect password", 405

        # update user data with LinkedIn access token
        customers_collection.update({"email": email},
        {"$set": {"linkedin_token": [linkedin_token]}})

        return "Your LinkedIn profile has been successfully added", 200

    def add_facebook(self, email, password, facebook_token):
        try:
            customers_collection.find_one({"email": email})
        except:
            return "Email does not exist", 402
        # confirm email-password match
        entry = Entry()
        correct_password = entry.verify_password(email, password)
        if not correct_password:
            return "Incorrect password", 405

        # update user data with LinkedIn access token
        customers_collection.update({"email": email},
        {"$set": {"facebook_token": [facebook_token]}})

        return "Your Facebook profile has been successfully added", 200

