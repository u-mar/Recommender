from flask import Flask,render_template,request
import pickle
import numpy as np
import random

popular_df = pickle.load(open('models/popular.pkl','rb'))
pt = pickle.load(open('models/pt.pkl','rb'))
books = pickle.load(open('models/books.pkl','rb'))
similarity_scores = pickle.load(open('models/similarity_scores.pkl','rb'))

app = Flask(__name__,template_folder='template')

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes= list(popular_df['num_ratings'].values),
                           rating=[round(num,2) for num in popular_df['avg_rating'].values]
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html',data=data)


def movie_rater(movie_df,num=5):
    user = 611
    rating_list = []
    for i in range(num):
        movie = movie_df.sample(1)
        print(movie['title'].values[0])
        print()
        rate = input('How do you rate this movie on a scale of 1-5, press n if you have not seen :' )
        print()
        if rate == 'n':
            continue
        else:
            rate = int(rate)
            rating_dict = {'userId':user,'movieId':movie['movieId'].iloc[0],'rating':rate}
            rating_list.append(rating_dict)
            

    return rating_list



@app.route('/shelf', methods=['post', 'get'])
def shelf():
    # Assuming `books` is your dataset
    
    # Select a random subset of books (e.g., 10 books)
    num_books_to_display = 10
    random_books_indices = random.sample(range(len(books)), num_books_to_display)
    
    random_book_names = [books['Book-Title'][i] for i in random_books_indices]
    random_authors = [books['Book-Author'][i] for i in random_books_indices]
    random_images = [books['Image-URL-M'][i] for i in random_books_indices]
    
    return render_template('shelf.html',
                           book_name=random_book_names,
                           author=random_authors,
                           image=random_images)






if __name__ == '__main__':
    app.run(debug=True)
