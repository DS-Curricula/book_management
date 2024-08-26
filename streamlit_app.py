import streamlit as st
import requests
import pandas as pd
import random
import string
from datetime import datetime

# Define the base URL of the FastAPI application
BASE_URL = 'http://127.0.0.1:8000/api'


# Function to generate a random secret key
def generate_secret_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


# Store the secret key in the session state when the app first loads
if 'secret_key' not in st.session_state:
    st.session_state['secret_key'] = generate_secret_key()


# Function to validate secret key
def validate_secret_key(input_key):
    return input_key == st.session_state['secret_key']


# Dashboard for managing Authors
def authors_dashboard():
    st.title("Authors Management")

    # Display existing authors
    st.subheader("Existing Authors")
    response = requests.get(f"{BASE_URL}/authors/")
    if response.status_code == 200:
        authors = response.json()
        df_authors = pd.DataFrame(authors)
        st.dataframe(df_authors, use_container_width=True)
    else:
        st.error("Failed to fetch authors.")

    # Form to add a new author
    st.subheader("Add a New Author")
    new_author_name = st.text_input("Author Name")
    input_key = st.text_input("Enter Secret Key", type="password")
    if st.button("Add Author"):
        if new_author_name.strip() == "":
            st.error("Author name cannot be empty.")
        elif validate_secret_key(input_key):
            response = requests.post(f"{BASE_URL}/authors/", json={"name": new_author_name})
            if response.status_code == 200:
                st.success(f"Author '{new_author_name}' added successfully!")
            else:
                st.error(f"Failed to add author: {response.json()['detail']}")
        else:
            st.error("Invalid Secret Key")


# Dashboard for managing Books
def books_dashboard():
    st.title("Books Management")

    # Display existing books
    st.subheader("Existing Books")
    response = requests.get(f"{BASE_URL}/books/")
    if response.status_code == 200:
        books = response.json()

        # Fetch existing authors for mapping author IDs to names
        authors_response = requests.get(f"{BASE_URL}/authors/")
        if authors_response.status_code == 200:
            authors = authors_response.json()
            author_id_to_name = {author['id']: author['name'] for author in authors}

            # Replace author IDs with names in the books data
            for book in books:
                book['author'] = author_id_to_name.get(book['author_id'], 'Unknown')
                del book['author_id']  # Remove the ID from the DataFrame

            df_books = pd.DataFrame(books)
            st.dataframe(df_books, use_container_width=True)
        else:
            st.error("Failed to fetch authors for mapping.")
    else:
        st.error("Failed to fetch books.")

    # Fetch existing authors for the dropdown
    st.subheader("Add a New Book")
    authors_response = requests.get(f"{BASE_URL}/authors/")
    if authors_response.status_code == 200:
        authors = authors_response.json()
        author_options = {author['name']: author['id'] for author in authors}
        selected_author_name = st.selectbox("Select Author", options=list(author_options.keys()))
        selected_author_id = author_options[selected_author_name]
    else:
        st.error("Failed to fetch authors for dropdown.")

    # Form to add a new book
    new_book_title = st.text_input("Title")
    new_book_average_rating = st.number_input("Average Rating", min_value=0.0, max_value=5.0, step=0.01)
    new_book_genres = st.text_input("Genres (comma-separated IDs)")

    # Get the current year and set the minimum year for the year input
    current_year = datetime.now().year
    min_year = 1440  # Example of a reasonable year; adjust as needed
    new_book_year = st.number_input("Year", min_value=min_year, max_value=current_year, step=1)

    input_key = st.text_input("Enter Secret Key", type="password")

    if st.button("Add Book"):
        if new_book_title.strip() == "" or new_book_genres.strip() == "":
            st.error("Title and Genres cannot be empty.")
        elif validate_secret_key(input_key):
            genres_list = [int(g.strip()) for g in new_book_genres.split(',') if g.strip().isdigit()]
            book_data = {
                "title": new_book_title,
                "author_id": selected_author_id,
                "book_link": "",  # Assuming book_link is optional for creation
                "genres": genres_list,
                "average_rating": new_book_average_rating,
                "published_year": new_book_year
            }
            response = requests.post(f"{BASE_URL}/books/", json=book_data)
            if response.status_code == 200:
                st.success(f"Book '{new_book_title}' added successfully!")
            else:
                st.error(f"Failed to add book: {response.json()['detail']}")
        else:
            st.error("Invalid Secret Key")


# Main function
def main():
    st.sidebar.title("Secret Key Management")
    if st.sidebar.button("Generate New Secret Key"):
        st.session_state['secret_key'] = generate_secret_key()

    st.sidebar.write(f"Secret Key: {st.session_state['secret_key']}")

    st.sidebar.title("Dashboard Navigation")
    dashboard = st.sidebar.selectbox("Choose a Dashboard", ("Books", "Authors"))

    if dashboard == "Books":
        books_dashboard()
    elif dashboard == "Authors":
        authors_dashboard()


if __name__ == "__main__":
    main()
