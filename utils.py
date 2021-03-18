from pymongo import MongoClient

mongo_client = MongoClient("mongodb://mdb:27017")

# create a new mongo database using pymongo
mongo_db = mongo_client.bradb
publishing_collection = mongo_db["publishing"]
customers_collection = mongo_db["customers"]
listening_collection = mongo_db["listening"]


def retrieve_token(email):
    """
    To confirm user has access to account, and also retrieve the token key and secret
    """
    accounts = customers_collection.find({"email":email})[0]["accounts"]
    # extract needed details and save
    account_details = [(i['media_type'], i['media_username'], i['token_key'], i['token_secret'], i["sm_profile_id"])
    for i in accounts if i['media_type']==media_type and i['media_username']==media_username]
    #token_key = account_details[0][2]
    #token_secret = account_details[0][3]
    #sm_profile_id = account_details[0][4]
    return account_details


def retrieve_current_time_scheduled_posts(email):
    """
    confirm user has access to account, and find posts with the email = email provided in params
    """
    all_posts = publishing_collection.find({"email": email})
    current_time_scheduled_posts = [(i["_id"], i["body"], i["media_username"], i["media_type"],
    i["sm_profile_id"], i["token_key"], i["token_secret"])
    for i in all_posts if i["post_type"]=="scheduled" and i["post_datetime"]==post_datetime]

    return current_time_scheduled_posts