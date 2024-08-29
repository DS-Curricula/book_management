import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

# Define the base URL of the FastAPI application
BASE_URL = 'http://127.0.0.1:8000/api'

api_key_input = st.text_input("Enter API Key", type="password")


def validate_api_key(api_key):
    headers = {"api-key": api_key}
    response = requests.get(f"{BASE_URL}/validate_key/", headers=headers)
    print(f"Request Headers: {headers}")
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    return response.status_code == 200


# Helper functions for API communication
def get_authors():
    response = requests.get(f"{BASE_URL}/authors/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch authors.")
        return []


def add_author(api_key, name):
    headers = {"api-key": api_key}
    response = requests.post(f"{BASE_URL}/authors/", json={"name": name}, headers=headers)
    if response.status_code == 200:
        st.success(f"Author '{name}' added successfully!")
    else:
        st.error(f"Failed to add author: {response.json().get('detail', 'Unknown error')}")


def update_author(api_key, author_id, name):
    headers = {"api-key": api_key}
    response = requests.put(f"{BASE_URL}/authors/{author_id}", json={"name": name}, headers=headers)
    if response.status_code == 200:
        st.success(f"Author '{name}' updated successfully!")
    else:
        st.error(f"Failed to update author: {response.json().get('detail', 'Unknown error')}")


def delete_author(api_key, author_id):
    headers = {"api-key": api_key}
    response = requests.delete(f"{BASE_URL}/authors/{author_id}", headers=headers)
    if response.status_code == 200:
        st.success("Author deleted successfully!")
    else:
        st.error(f"Failed to delete author: {response.json().get('detail', 'Unknown error')}")


def get_books():
    response = requests.get(f"{BASE_URL}/books/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch books.")
        return []


def add_book(api_key, book_data):
    headers = {"api-key": api_key}
    response = requests.post(f"{BASE_URL}/books/", json=book_data, headers=headers)
    if response.status_code == 200:
        st.success(f"Book '{book_data['title']}' added successfully!")
    else:
        st.error(f"Failed to add book: {response.json().get('detail', 'Unknown error')}")


def update_book(api_key, book_id, book_data):
    headers = {"api-key": api_key}
    response = requests.put(f"{BASE_URL}/books/{book_id}", json=book_data, headers=headers)
    if response.status_code == 200:
        st.success(f"Book '{book_data['title']}' updated successfully!")
    else:
        st.error(f"Failed to update book: {response.json().get('detail', 'Unknown error')}")


def delete_book(api_key, book_id):
    headers = {"api-key": api_key}
    response = requests.delete(f"{BASE_URL}/books/{book_id}", headers=headers)
    if response.status_code == 200:
        st.success("Book deleted successfully!")
    else:
        st.error(f"Failed to delete book: {response.json().get('detail', 'Unknown error')}")


# Dashboard for managing Authors
def authors_dashboard(api_key):
    st.title("Authors Management")

    # Display existing authors
    st.subheader("Existing Authors")
    authors = get_authors()
    df_authors = pd.DataFrame(authors)
    st.dataframe(df_authors, use_container_width=True)

    # Form to add a new author
    st.subheader("Add New Author")
    new_author_name = st.text_input("Author Name")

    if st.button("Add Author"):
        if new_author_name.strip():
            add_author(api_key, new_author_name)
        else:
            st.error("Author name cannot be empty.")

    # Choose an action to perform
    action = st.radio("What would you like to do?", options=["Update Author", "Delete Author"])

    if action == "Update Author":
        selected_author = st.selectbox("Select Author to Update", options=[author['name'] for author in authors])
        new_name = st.text_input("New Author Name", value=selected_author)

        if st.button("Update Author"):
            author_id = next((author['id'] for author in authors if author['name'] == selected_author), None)
            update_author(api_key, author_id, new_name)

    elif action == "Delete Author":
        author_to_delete = st.selectbox("Select Author to Delete", options=[author['name'] for author in authors])
        if st.button("Delete Author"):
            author_id = next((author['id'] for author in authors if author['name'] == author_to_delete), None)
            delete_author(api_key, author_id)


# Dashboard for managing Books
def books_dashboard(api_key):
    st.title("Books Management")

    # Display existing books
    st.subheader("Existing Books")
    books = get_books()
    authors = get_authors()

    author_id_to_name = {author['id']: author['name'] for author in authors}
    for book in books:
        book['author'] = author_id_to_name.get(book['author_id'], 'Unknown')
        del book['author_id']

    df_books = pd.DataFrame(books)
    st.dataframe(df_books, use_container_width=True)

    # Form to add a new book
    st.subheader("Add New Book")
    new_book_title = st.text_input("Title")
    selected_author_name = st.selectbox("Select Author", options=[author['name'] for author in authors],
                                        key="select_author_add")
    new_book_average_rating = st.number_input("Average Rating", min_value=0.0, max_value=5.0, step=0.01)
    new_book_genres = st.text_input("Genres (comma-separated IDs)")
    new_book_year = st.number_input("Year", min_value=1440, max_value=datetime.now().year, step=1)

    if st.button("Add Book"):
        if new_book_title.strip() and new_book_genres.strip():
            genres_list = [int(g.strip()) for g in new_book_genres.split(',') if g.strip().isdigit()]
            selected_author_id = next((author['id'] for author in authors if author['name'] == selected_author_name),
                                      None)
            book_data = {
                "title": new_book_title,
                "author_id": selected_author_id,
                "book_link": "",  # Assuming book_link is optional for creation
                "genres": genres_list,
                "average_rating": new_book_average_rating,
                "published_year": new_book_year
            }
            add_book(api_key, book_data)
        else:
            st.error("Title and Genres cannot be empty.")

    # Choose an action to perform
    action = st.radio("What would you like to do?", options=["Update Book", "Delete Book"], key="radio_action")

    if action == "Update Book":
        selected_book = st.selectbox("Select Book to Update", options=[book['title'] for book in books],
                                     key="select_book_update")

        if selected_book:
            book = next((book for book in books if book['title'] == selected_book), None)
            new_book_title = st.text_input("Title", value=book['title'])
            selected_author_name = st.selectbox("Select Author", options=[author['name'] for author in authors],
                                                index=[author['name'] for author in authors].index(book['author']),
                                                key="select_author_update")
            new_book_average_rating = st.number_input("Average Rating", min_value=0.0, max_value=5.0, step=0.01,
                                                      value=book['average_rating'])
            new_book_genres = st.text_input("Genres (comma-separated IDs)",
                                            value=', '.join(str(g) for g in book['genres']))
            new_book_year = st.number_input("Year", min_value=1440, max_value=datetime.now().year, step=1,
                                            value=book['published_year'])
            book_id = book['id']

            if st.button("Update Book"):
                genres_list = [int(g.strip()) for g in new_book_genres.split(',') if g.strip().isdigit()]
                book_data = {
                    "title": new_book_title,
                    "author_id": next((author['id'] for author in authors if author['name'] == selected_author_name),
                                      None),
                    "book_link": book.get('book_link', ""),
                    "genres": genres_list,
                    "average_rating": new_book_average_rating,
                    "published_year": new_book_year
                }
                update_book(api_key, book_id, book_data)

    elif action == "Delete Book":
        book_to_delete = st.selectbox("Select Book to Delete", options=[book['title'] for book in books],
                                      key="select_book_delete")
        if st.button("Delete Book"):
            book_id = next((book['id'] for book in books if book['title'] == book_to_delete), None)
            delete_book(api_key, book_id)


# Visualizations Dashboard
def visualizations_dashboard():
    st.title("Visualizations Dashboard")

    books = get_books()
    authors = get_authors()

    if books:
        df_books = pd.DataFrame(books)
        if 'author_id' in df_books.columns:
            author_id_to_name = {author['id']: author['name'] for author in authors}
            df_books['author'] = df_books['author_id'].map(author_id_to_name)
            df_books.drop('author_id', axis=1, inplace=True)

        st.subheader("Books by Year")
        books_by_year = df_books.groupby('published_year').size().reset_index(name='Count')
        fig_years = px.bar(books_by_year, x='published_year', y='Count', title='Number of Books by Year')
        st.plotly_chart(fig_years, use_container_width=True)

        st.subheader("Books by Author")
        books_by_author = df_books.groupby('author').size().reset_index(name='Count')
        fig_authors = px.bar(books_by_author, x='author', y='Count', title='Number of Books by Author')
        st.plotly_chart(fig_authors, use_container_width=True)

    else:
        st.warning("No book data available for visualizations.")


# Main app logic
st.sidebar.title("Navigation")
option = st.sidebar.selectbox("Choose a dashboard", ["Authors Dashboard", "Books Dashboard", "Visualizations"])
if option == "Visualizations":
    visualizations_dashboard()
if api_key_input and validate_api_key(api_key_input):
    if option == "Authors Dashboard":
        authors_dashboard(api_key_input)
    elif option == "Books Dashboard":
        books_dashboard(api_key_input)
else:
    st.error("Invalid API Key or API Key is missing.")
