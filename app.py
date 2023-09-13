from email.mime import image
from flask import Flask,render_template,request,redirect,session
import pickle
import numpy as np
import random
import requests
import psycopg2
import pandas as pd
import json


dataa = pickle.load(open('pop.pkl','rb'))

monkey = pd.read_csv('real.csv')
auto = monkey['title'].unique().tolist()
auto = json.dumps(auto)


app = Flask(__name__,template_folder='template')
app.secret_key = 'crazyyworld'

DB_HOST = 'recommende-server.postgres.database.azure.com'
DB_NAME = 'recommende-database'
DB_USER = 'atypbgzfta'
DB_PASSWORD = 'LR5M58112OAFE2G7$'

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        self.create_table()
        self.rate_table()

    def create_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS userss (
                    userId SERIAL PRIMARY KEY,
                    username TEXT,
                    password TEXT
                )
            """)
            self.conn.commit()
    def rate_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate (
                userId INT REFERENCES userss(userId),
                rating FLOAT,
                title VARCHAR(255),
                tmdbId INT,
                CONSTRAINT unique_user_movie UNIQUE (userId, tmdbId)
            )
        """)
        self.conn.commit()

    def sign(self,username,password):
        with self.conn.cursor() as cursor:
            cursor.execute("INSERT INTO userss (username, password) VALUES (%s, %s)", (username, password))
            self.conn.commit()


    
    def log(self, username, password):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT userId,username, password FROM userss WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user and user[2] == password:
                return True,user
            else:
                return False
            
    def rate(self,userId,rating,title,movie):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('INSERT INTO rate (userId,rating,title,tmdbId) VALUES(%s,%s,%s,%s)',(userId,rating,title,movie))
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()

db = Database()


def fetch_poster(movie_id):
     url = "https://api.themoviedb.org/3/movie/{}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US".format(movie_id)
     data=requests.get(url)
     data=data.json()
     poster_path = data['poster_path']
     full_path = "https://image.tmdb.org/t/p/w500/"+poster_path
     return full_path

def fetch(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=5ef4f9a6c8f0a6fb8ccd12e5be032336&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    if 'poster_path' in data:
        poster_path = data['poster_path']
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    else:
        return 'https://image.tmdb.org/t/p/w500//fB0cGiEOngfsfyDHXIpFOmEwFgi.jpg'


@app.route('/')
def index():
    return render_template('index.html',
                           image = [fetch(int(i)) for i in dataa['tmdbid']]
                           )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html',auto=auto)

@app.route('/recommend_books',methods=['post'])
def recommend():
    index=df[df['title']==movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector:vector[1])
    data = []
    for i in distance[1:7]:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)


    return render_template('recommend.html',data=data,auto=auto)


@app.route('/shelf', methods=['GET', 'POST'])
def shelf():
    userId = session.get('userId')
    num_books_to_display = 5
    random_books_indices = random.sample(range(len(monkey['title'])), num_books_to_display)
    
    random_name = [monkey['title'][i] for i in random_books_indices]
    random_id = [int(monkey['tmdbId'][i]) for i in random_books_indices]
    images = []

    if request.method == 'POST':
        for i in range(1):
            rating_name = f"user_input{i}"
            rating = request.form[rating_name]
            db.rate(userId,rating,random_name[i],random_id[i])

    for i in range(5):
        images.append(fetch_poster(random_id[i]))

    return render_template('shelf.html',
                           image=images,
                           book_name=random_name,
                          )

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']

    db.sign(username,password)

    return render_template('/user.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    logged,user = db.log(username,password)
    if logged:
        session['userId'] = user[0]
        return redirect('/shelf')
    else:
        return '<h1> Failed to Login </h1>'

if __name__ == '__main__':
    app.run(debug=True)
