import streamlit as st
import pickle
import pandas as pd
import requests

# Function to fetch movie poster URL from TMDb API
@st.cache
def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=7ea4970a17e0c6187e71a2894670c7ec')
    if response.status_code == 200:
        data = response.json()
        if 'poster_path' in data:
            return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
    return None

# Function to recommend movies based on selected movie
@st.cache
def recommend(movie, movies, similarity):
    movie_index = movies[movies['title'] == movie].index
    if len(movie_index) == 0:
        return [], []  # Handle case where movie is not found
    movie_index = movie_index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        poster_url = fetch_poster(movie_id)
        if poster_url:
            recommended_movies_posters.append(poster_url)
    return recommended_movies, recommended_movies_posters

# Load data
@st.cache
def load_data(movie_dict_path, similarity_path):
    with open(movie_dict_path, 'rb') as f:
        movie_dict = pickle.load(f)
    with open(similarity_path, 'rb') as f:
        similarity = pickle.load(f)
    movies = pd.DataFrame(movie_dict)
    return movies, similarity

# Streamlit UI
def main():
    st.title('Movie Recommender System')

    # Load data
    movie_dict_path = 'movie_dict.pkl'
    similarity_path = 'similarity.pkl'
    movies, similarity = load_data(movie_dict_path, similarity_path)

    # Select a movie
    selected_movie_name = st.selectbox('Select a movie:', movies['title'].values)

    # Recommend button
    if st.button('Recommend'):
        names, posters = recommend(selected_movie_name, movies, similarity)
        if names:
            num_recommendations = min(len(names), 5)
            cols = st.beta_columns(num_recommendations)
            for i in range(num_recommendations):
                with cols[i]:
                    st.text(names[i])
                    st.image(posters[i] if i < len(posters) else 'No poster available')

if __name__ == "__main__":
    main()
