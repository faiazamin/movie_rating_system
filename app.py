from flask import Flask, request, jsonify
import json
import config

app = Flask(__name__)

# Sample data
users = [
    {"id": 1, "name": "John Doe", "phone": "11111111111", "password": "pass1", "email": "john_doe@gmail.com"},
    {"id": 2, "name": "Jane Doe", "phone": "22222222222", "password": "pass2", "email": "jane_doe@gmail.com"},
    {"id": 3, "name": "Mark Doe", "phone": "3333333333", "password": "pass3", "email": "mark_doe@gmail.com"},
    {"id": 4, "name": "Macy Doe", "phone": "4444444444", "password": "pass4", "email": "macy_doe@gmail.com"}
]

movies = [
    {"id": 1, "name": "Home Alone", "genre": "Comedy", "rating": "PG", "release_date": "01-04-1996"},
    {"id": 2, "name": "The Godfather", "genre": "Crime", "rating": "R", "release_date": "01-04-1972"},
    {"id": 3, "name": "Avengers: Endgame", "genre": "Action", "rating": "PG", "release_date": "01-04-2019"}
]

ratings = [
    {"id": 1, "user_id": 1, "movie_id": 1, "rating": 5.0},
    {"id": 2, "user_id": 1, "movie_id": 2, "rating": 4.0},
    {"id": 3, "user_id": 1, "movie_id": 3, "rating": 3.3},
    {"id": 4, "user_id": 2, "movie_id": 1, "rating": 5.0},
    {"id": 5, "user_id": 2, "movie_id": 3, "rating": 4.5},
    {"id": 6, "user_id": 3, "movie_id": 1, "rating": 1.6},
    {"id": 7, "user_id": 3, "movie_id": 2, "rating": 0.0},
    {"id": 8, "user_id": 3, "movie_id": 3, "rating": 3.4},
    {"id": 9, "user_id": 4, "movie_id": 2, "rating": 4.5}
]

# Authentication
def authenticate(email, password):
    # get users from database
    response = request.get(url = config.users)
    all_users = response.json()['users']
    for user in all_users:
        if user['email'] == email and user['password'] == password:
            with open('current_user.json','w') as current_user:
                current_user.write(user)
            return user
    return None

# Authorization
def authorize(user_id):
    try:
        with open('current_user.json','r') as current_user:
            user = json.load(current_user)
            if user==[]:
                return False
            elif user_id == user['id']:
                return True
    except:
        return False


# Routes

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = authenticate(email, password)
    if user:
        return jsonify({'user_id': user['id'], 'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# Add a movie
@app.route('/movies', methods=['POST'])
def add_movie():
    if not authorize(request.json.get('user_id')):
        return jsonify({'error': 'Unauthorized access'}), 403
    movie = request.json
    movies.append(movie)
    return jsonify({'message': 'Movie added successfully'})

# View all movies
@app.route('/movies', methods=['GET'])
def get_movies():
    response = request.get(config.movies)
    movies = response.json()['movies']
    return jsonify(movies)

# Rate a movie
@app.route('/rate', methods=['POST'])
def rate_movie():
    data = request.json
    user_id = data.get('user_id')
    movie_id = data.get('movie_id')
    rating = data.get('rating')
    if not authorize(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    for rate in ratings:
        if rate['user_id'] == user_id and rate['movie_id'] == movie_id:
            rate['rating'] = rating
            return jsonify({'message': 'Rating updated successfully'})
    ratings.append({'id': len(ratings) + 1, 'user_id': user_id, 'movie_id': movie_id, 'rating': rating})
    return jsonify({'message': 'Rating added successfully'})

# Search a movie
@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = [movie for movie in movies if movie['id'] == movie_id]
    if len(movie) == 0:
        return jsonify({'error': 'Movie not found'}), 404
    movie_data = movie[0]
    movie_ratings = [rating['rating'] for rating in ratings if rating['movie_id'] == movie_id]
    if len(movie_ratings) == 0:
        avg_rating = 0
    else:
        avg_rating = sum(movie_ratings) / len(movie_ratings)
    movie_data['average_rating'] = avg_rating
    return jsonify(movie_data)

if __name__ == '__main__':
    app.run(debug=True)
