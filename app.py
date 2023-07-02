from flask import Flask, request, render_template
from flask import Flask, render_template,redirect, request,url_for,jsonify,send_file
import openai
import json
from pymongo.mongo_client import MongoClient
uri = "mongodb://msukeerthirajeevi:5XUlZyGz8wF3MB7A@ac-t87uhto-shard-00-00.sdw7soj.mongodb.net:27017,ac-t87uhto-shard-00-01.sdw7soj.mongodb.net:27017,ac-t87uhto-shard-00-02.sdw7soj.mongodb.net:27017/?ssl=true&replicaSet=atlas-ry4tco-shard-0&authSource=admin&retryWrites=true&w=majority"



# Set up OpenAI GPT-3 Sandbox API credentials
openai.api_key = 'API-KEY'

client = MongoClient(uri)
mydb = client["movie-recommender"]
users_collection=mydb.users

app = Flask(__name__,static_folder='dist')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login',methods=['GET', 'POST'])
def viewloginpage():
    return render_template('signup.html')
   
   
@app.route('/signup',methods=['GET', 'POST'])
def view_signuppage():
    return render_template('signup.html')

@app.route('/processignup',methods=['GET', 'POST'])
def process():
    username = request.form['txt']
    email = request.form['email']
    password = request.form['pswd']

    # Check if user already exists in the collection
    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        error_message = f"User '{username}' already exists!"
        return render_template('signup.html', error=error_message)

    # Create a document to insert into the collection
    document = {
        'username': username,
        'email': email,
        'password': password
    }

    # Insert the document into the collection
    users_collection.insert_one(document)

    return render_template('signup.html')

@app.route('/authenticate', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['pswd']
    
    user = users_collection.find_one({"username": email, "password": password})
    print("username=")
    print(user['username'])
    if user:
        return render_template('search-bar.html',username=user['username'])
    else:
        return render_template('signup.html',error="Wrong username or password.")


@app.route('/search', methods=['GET','POST'])
def search():
    username="sukee"
    # Retrieve the data from the request
    keywords = request.args.get('keywords')
    username = request.args.get('username')
    mycollection = mydb[username]

    projection = {"_id": 0}
    liked_movies = mycollection.find({}, projection)
    liked_movies_str = ', '.join([f"{doc['movie']} (Rating: {doc['rating']})" for doc in liked_movies])
    
    # Do something with the retrieved data (e.g., perform a search)
    print('Search keywords:', keywords)
    
    user_input=f"""
User: Generate 5 movie recommendations based on these keywords{keywords} ? Here are my
liked movies and the ratings out of 5 I gave to them: {liked_movies_str}
give movie name and description about it, leave two lines space after each movie
"""
    print(user_input)
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=user_input,
    max_tokens=1000,
    n=1,
    temperature=0.7,
    stop=None,
    frequency_penalty=0.0,
    presence_penalty=0.0
    )
    print(" types(person)")

    # Extract the recommended movies from the generated response
    recommendations = [choice['text'].strip() for choice in response.choices]
    recommendations_str = '<br>'.join(recommendations)
    recommendations_str = recommendations_str.replace('\n', '<br>')

    # Redirect or render a response as needed
    return render_template('display-result.html',results=recommendations_str,username=username)



if __name__ == '__main__':
    app.run()
