from fastapi import Body, FastAPI

app = FastAPI()

@app.get("/api-endpoint")
async def first_api():
    return {'message': 'Hola mundo'}

# Para ejecutar la aplicación, usar el siguiente comando:
# uvicorn books:app --reload 

# Luego se puede acceder a la API en http://127.0.0.1:8000/

# La documentación automática estará disponible en: 
# http://127.0.0.1:8000/docs

BOOKS = [
    {'Title': 'Harry Potter', 'Author': 'Author One', 'Pages': 150, 'Rating': 4.5, 'Category': 'Fiction'},
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
# http://127.0.0.1:8000/books/?category=Fiction
@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('Category').casefold() == category.casefold():
            books_to_return.append(book)
    
    return books_to_return

# Get all books from a specific author using query parameters
@app.get("/books/byauthor/")
async def read_books_by_author_query(author : str):
    books_to_return = []
    for book in BOOKS:
        if book.get("Author").casefold() == author.casefold():
            books_to_return.append(book)
    return books_to_return

# Get all books from a especific author using path parameters and an especific category using query params
@app.get("/books/{book_author}")
async def read_book_by_author_path_by_category_query(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        print(book)
        print(book_author)
        print(category)
        if book.get("Author").casefold() == book_author.casefold() and book.get("Category").casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

@app.post("/books/create")  
async def create_book(new_book=Body()):
    BOOKS.append(new_book)
    return {'message':'Book created'}

@app.put("/books/update")
async def update_book(updated_book=Body()):
    for i, book in enumerate(BOOKS):
        if book.get("Title").casefold() == updated_book.get("Title").casefold():
            BOOKS[i] = updated_book
            return {'message': 'Book updated'}
    return {'message': 'Book not found'}

@app.delete("/books/delete/{title}")
async def delete_book(title: str):
    for i, book in enumerate(BOOKS):
        if book.get("Title").casefold() == title.casefold():
            BOOKS.pop(i)
            return {'message': f'Book {title} deleted'}
    return {'message': 'Book not found'}