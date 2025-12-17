from fastapi import FastAPI

app = FastAPI()

@app.get("/api-endpoint")
async def first_api():
    return {'message': 'Hola mundo'}

# Para ejecutar la aplicación, usa el siguiente comando:
# uvicorn books:app --reload 

# Luego, puedes acceder a la API en http://127.0.0.1:8000/

# La documentación automática estará disponible en: 
# http://127.0.0.1:8000/docs

BOOKS = [
    {'Title': 'Title One', 'Author': 'Author One', 'Pages': 150, 'Rating': 4.5, 'Category': 'Fiction'},
    {'Title': 'Title Two', 'Author': 'Author Two', 'Pages': 200, 'Rating': 4.0, 'Category': 'Non-Fiction'},
    {'Title': 'Title Three', 'Author': 'Author Three', 'Pages': 300, 'Rating': 4.8, 'Category': 'Science Fiction'},
    {'Title': 'Title Four', 'Author': 'Author Four', 'Pages': 250, 'Rating': 3.9, 'Category': 'Fantasy'},
    {'Title': 'Title Five', 'Author': 'Author Five', 'Pages': 180, 'Rating': 4.2, 'Category': 'Fiction'},
]

@app.get("/books")
async def read_all_books():
    return BOOKS

# Path Paramters
# http://127.0.0.1:8000/books/HarryPotter
@app.get("/books/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get('Title').casefold() == book_title.casefold():
            return book
        
# Query Parameters
# http://127.0.0.1:8000/books/?category=ciencia
@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('Category').casefold() == category.casefold():
            books_to_return.append(book)
    
    return books_to_return

@app.get("/books/byauthor/")
async def read_books_by_author(author : str):
    books_to_return = []
    for book in BOOKS:
        if book.get("Author").casefold() == author.casefold():
            books_to_return.append(book)
    return books_to_return