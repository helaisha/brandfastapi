from fastapi import FastAPI, Request, Body
import requests
import uvicorn
import bcrypt
import datetime
from pymongo import MongoClient
#import psycopg2
#import psycopg2.extras
import tweepy
from publishing import Scheduling, QuickPost
from access import Entry, AddAccount

app = FastAPI(title="Digital Marketing API Prototype", description="API for Social media management and social media listening", version="1.0.0")


@app.get("/", tags=["Home"])
async def home():

    return "Hello World"

# signup endpoint
@app.post("/signup", tags=["Access"])
async def access(fullname: str, email: str, password: str):
    entry = Entry()
    signup_result = entry.signup(fullname, email, password)
    return signup_result

# login endpoint
@app.post("/login/{email}", tags=["Access"])
async def access(email: str, password: str):
    entry = Entry()
    login_result = entry.login(email, password)
    return login_result

# add Twitter account endpoint
@app.post("/add_twitter", tags=["Access"])
async def access(email: str, password: str, twitter_key: str, twitter_secret: str):
    add_account = AddAccount()
    twitter_result = add_account.add_twitter(email, password, twitter_key, twitter_key)
    return twitter_result

# add LinkedIn account endpont
@app.post("/add_linkedin", tags=["Access"])
async def access(email: str, password: str, linkedin_token: str):
    add_account = AddAccount()
    linkedin_result = add_account.add_linkedin(email, password, linkedin_token)
    return linkedin_result

# add Facebook account endpont
@app.post("/add_facebook", tags=["Access"])
async def access(email: str, password: str, facebook_token: str):
    add_account = AddAccount()
    facebook_result = add_account.add_facebook(email, password, facebook_token)
    return facebook_result

# schedule post endpoint
@app.post("/schedule_post", tags=["Publishing"])
async def publishing(email: str, password: str, post_datetime: str, media_type: str, media_username: str, message_text: str):
    scheduling = Scheduling()
    schedule_post_response = scheduling.schedule_post(email, password, post_datetime, media_type, media_username, message_text)
    return schedule_post_response

# see all scheduled post endpoint
@app.get("/see_schedule", tags=["Publishing"])
async def publishing(email: str, password: str):
    scheduling = Scheduling()
    scheduled_posts = scheduling.see_schedule(email, password)
    return scheduled_posts

# delete scheduled post endpoint
@app.post("/kill_scheduled_post", tags=["Publishing"])
async def publishing(email: str, password: str, post_id: str):
    scheduling = Scheduling()
    kill_scheduled_response = scheduling.kill_scheduled_post(email, password, post_id)
    return kill_scheduled_response

# change schedule post endpoint
@app.post("/change_schedule", tags=["Publishing"])
async def publishing(email:str, password:str, post_id:str, new_message_text:str, post_datetime:str):
    scheduling = Scheduling()
    change_schedule_response = scheduling.change_schedule(email, password, post_id, new_message_text, post_datetime)
    return change_schedule_response

# get published posts endpoint
@app.get("/get_posts", tags=["Publishing"])
async def publishing(email: str, password: str, media_type: str, media_username: str):
    scheduling = Scheduling()
    published_posts = scheduling.get_posts(email, password, media_type, media_username)
    return published_posts

# publish Twitter scheduled post endpoint
@app.post("/twitter_schedule_publish", tags=["Publishing"])
async def publishing(email: str, password: str, media_username: str, post_datetime: str):
    scheduling = Scheduling()
    twitter_publish_post_response = scheduling.twitter_schedule_publish(email, password, media_username, post_datetime)
    return twitter_publish_post_response

# publish LinkedIn scheduled post endpoint
@app.post("/linkedin_schedule_publish", tags=["Publishing"])
async def publishing(email: str, password: str, media_username: str, post_datetime: str):
    scheduling = Scheduling()
    linkedin_publish_post_response = scheduling.linkedin_schedule_publish(email, password, media_username, post_datetime)
    return linkedin_publish_post_response

# Make quick post to Twitter endpoint
@app.post("/twitter_quick_post", tags=["Publishing"])
async def publishing(email: str, password: str, media_username: str, message_text: str):
    quick_post = QuickPost()
    quick_post_response = quick_post.twitter_quick_post(email, password, media_username, message_text)
    return quick_post_response

# Make quick post to LinkedIn endpoint
@app.post("/linkedin_quick_post", tags=["Publishing"])
async def publishing(email: str, password: str, media_username: str, message_text: str):
    quick_post = QuickPost()
    quick_post_response = quick_post.linkedin_quick_post(email, password, media_username, message_text)
    return quick_post_response


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="info")
#python -m uvicorn main:app
