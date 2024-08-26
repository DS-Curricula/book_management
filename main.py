from fastapi import FastAPI
from routers import authors, books
from database import initialize_database

# Initialize FastAPI app
app = FastAPI(
    title="Book Management System",
    description="An API for managing books, authors, and genres.",
    version="1.0.0",
)

# Initialize the database tables
initialize_database()

# Include the routers
app.include_router(authors.router, prefix="/api/authors", tags=["Authors"])
app.include_router(books.router, prefix="/api/books", tags=["Books"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
