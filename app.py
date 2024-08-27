import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

# Define the base URL of the FastAPI application
BASE_URL = 'http://127.0.0.1:8000/api'


# Helper functions for API communication
def get_authors():
    response = requests.get(f"{BASE_URL}/authors/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch authors.")
        return []


def add_author(name):
    response = requests.post(f"{BASE_URL}/authors/", json={"name": name})
    if response.status_code == 200:
        st.success(f"Author '{name}' added successfully!")
    else:
        st.error(f"Failed to add author: {response.json().get('detail', 'Unknown error')}")


def update_author(author_id, name):
    response = requests.put(f"{BASE_URL}/authors/{author_id}", json={"name": name})
    if response.status_code == 200:
        st.success(f"Author '{name}' updated successfully!")
    else:
        st.error(f"Failed to update author: {response.json().get('detail', 'Unknown error')}")


def delete_author(author_id):
    response = requests.delete(f"{BASE_URL}/authors/{author_id}")
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


def add_book(book_data):
    response = requests.post(f"{BASE_URL}/books/", json=book_data)
    if response.status_code == 200:
        st.success(f"Book '{book_data['title']}' added successfully!")
    else:
        st.error(f"Failed to add book: {response.json().get('detail', 'Unknown error')}")


def update_book(book_id, book_data):
    response = requests.put(f"{BASE_URL}/books/{book_id}", json=book_data)
    if response.status_code == 200:
        st.success(f"Book '{book_data['title']}' updated successfully!")
    else:
        st.error(f"Failed to update book: {response.json().get('detail', 'Unknown error')}")


def delete_book(book_id):
    response = requests.delete(f"{BASE_URL}/books/{book_id}")
    if response.status_code == 200:
        st.success("Book deleted successfully!")
    else:
        st.error(f"Failed to delete book: {response.json().get('detail', 'Unknown error')}")


# Dashboard for managing Authors
def authors_dashboard():
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
            add_author(new_author_name)
        else:
            st.error("Author name cannot be empty.")

    # Choose an action to perform
    action = st.radio("What would you like to do?", options=["Update Author", "Delete Author"])

    if action == "Update Author":
        selected_author = st.selectbox("Select Author to Update", options=[author['name'] for author in authors])
        new_name = st.text_input("New Author Name", value=selected_author)

        if st.button("Update Author"):
            author_id = next((author['id'] for author in authors if author['name'] == selected_author), None)
            update_author(author_id, new_name)

    elif action == "Delete Author":
        author_to_delete = st.selectbox("Select Author to Delete", options=[author['name'] for author in authors])
        if st.button("Delete Author"):
            author_id = next((author['id'] for author in authors if author['name'] == author_to_delete), None)
            delete_author(author_id)


# Dashboard for managing Books
def books_dashboard():
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
    selected_author_name = st.selectbox("Select Author", options=[author['name'] for author in authors], key="select_author_add")
    new_book_average_rating = st.number_input("Average Rating", min_value=0.0, max_value=5.0, step=0.01)
    new_book_genres = st.text_input("Genres (comma-separated IDs)")
    new_book_year = st.number_input("Year", min_value=1440, max_value=datetime.now().year, step=1)

    if st.button("Add Book"):
        if new_book_title.strip() and new_book_genres.strip():
            genres_list = [int(g.strip()) for g in new_book_genres.split(',') if g.strip().isdigit()]
            selected_author_id = next((author['id'] for author in authors if author['name'] == selected_author_name), None)
            book_data = {
                "title": new_book_title,
                "author_id": selected_author_id,
                "book_link": "",  # Assuming book_link is optional for creation
                "genres": genres_list,
                "average_rating": new_book_average_rating,
                "published_year": new_book_year
            }
            add_book(book_data)
        else:
            st.error("Title and Genres cannot be empty.")

    # Choose an action to perform
    action = st.radio("What would you like to do?", options=["Update Book", "Delete Book"], key="radio_action")

    if action == "Update Book":
        selected_book = st.selectbox("Select Book to Update", options=[book['title'] for book in books], key="select_book_update")

        if selected_book:
            book = next((book for book in books if book['title'] == selected_book), None)
            new_book_title = st.text_input("Title", value=book['title'])
            selected_author_name = st.selectbox("Select Author", options=[author['name'] for author in authors],
                                                index=[author['name'] for author in authors].index(book['author']), key="select_author_update")
            new_book_average_rating = st.number_input("Average Rating", min_value=0.0, max_value=5.0, step=0.01,
                                                      value=book['average_rating'])
            new_book_genres = st.text_input("Genres (comma-separated IDs)", value=', '.join(str(g) for g in book['genres']))
            new_book_year = st.number_input("Year", min_value=1440, max_value=datetime.now().year, step=1,
                                            value=book['published_year'])
            book_id = book['id']

            if st.button("Update Book"):
                genres_list = [int(g.strip()) for g in new_book_genres.split(',') if g.strip().isdigit()]
                book_data = {
                    "title": new_book_title,
                    "author_id": next((author['id'] for author in authors if author['name'] == selected_author_name), None),
                    "book_link": book.get('book_link', ""),
                    "genres": genres_list,
                    "average_rating": new_book_average_rating,
                    "published_year": new_book_year
                }
                update_book(book_id, book_data)

    elif action == "Delete Book":
        book_to_delete = st.selectbox("Select Book to Delete", options=[book['title'] for book in books], key="select_book_delete")
        if st.button("Delete Book"):
            book_id = next((book['id'] for book in books if book['title'] == book_to_delete), None)
            delete_book(book_id)


# Dashboard for visualizations and summary metrics
def visualizations_dashboard():
    st.title("Dashboard")

    # Fetch data
    books = pd.DataFrame(get_books())
    authors = pd.DataFrame(get_authors())

    if books.empty or authors.empty:
        st.error("No data available to visualize.")
        return

    # Summary metrics
    st.subheader("Summary Metrics")
    num_books = books.shape[0]
    num_authors = authors.shape[0]
    avg_rating = books['average_rating'].mean()
    avg_published_year = books['published_year'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Books", num_books)
    col2.metric("Total Authors", num_authors)
    col3.metric("Average Book Rating", f"{avg_rating:.2f}")
    col4.metric("Average Published Year", f"{avg_published_year:.0f}")

    # Visualization: Number of Books per Author using Plotly
    st.subheader("Number of Books per Author")
    author_id_to_name = {author['id']: author['name'] for author in get_authors()}
    books['author_name'] = books['author_id'].map(author_id_to_name)
    books_per_author = books['author_name'].value_counts()

    fig = px.bar(books_per_author, x=books_per_author.index, y=books_per_author.values,
                 labels={'x': 'Author', 'y': 'Number of Books'}, title='Number of Books per Author')
    st.plotly_chart(fig)

    # Visualization: Average Rating by Year using Plotly
    st.subheader("Average Rating by Year")
    avg_rating_by_year = books.groupby('published_year')['average_rating'].mean().reset_index()

    fig = px.line(avg_rating_by_year, x='published_year', y='average_rating',
                  labels={'published_year': 'Year', 'average_rating': 'Average Rating'},
                  title='Average Rating by Year', markers=True)
    st.plotly_chart(fig)

    # Visualization: Distribution of Book Ratings using Plotly
    st.subheader("Distribution of Book Ratings")
    fig = px.histogram(books, x='average_rating', nbins=20,
                       labels={'average_rating': 'Rating'},
                       title='Distribution of Book Ratings')
    st.plotly_chart(fig)

    # Visualization: Top 10 Books by Rating using Plotly
    st.subheader("Top 10 Books by Rating")
    top_books = books.sort_values(by='average_rating', ascending=False).head(10)
    fig = px.bar(top_books, x='title', y='average_rating',
                 labels={'title': 'Book Title', 'average_rating': 'Average Rating'},
                 title='Top 10 Books by Rating')
    st.plotly_chart(fig)


# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a Page", options=["Authors Management", "Books Management", "Dashboard"])

if page == "Authors Management":
    authors_dashboard()
elif page == "Books Management":
    books_dashboard()
elif page == "Dashboard":
    visualizations_dashboard()
