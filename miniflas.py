#!/usr/bin/env python
from flask import Flask,request
app=Flask(__name__)

@app.route('/user/<username>')
def show_user_profile(username):
    #show the user profile for that user
    return 'User %s'%username
@app.route('/post/<int:post_id>')
def show_post(post_id):
    #show the post with the given id,the id is an integer
    return "Post %d"%post_id

@app.route('/')
def index():
    return 'Index Page'
@app.route('/hello')
def hello_word():
    return 'Hello,world'
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        do_the_login()
    else:
        show_the_login_form()
