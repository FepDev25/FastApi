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
    {'Title': 'Title One', 'Author': 'Author One', 'Pages': 150, 'Rating': 4.5, 'Genre': 'Fiction'},
    {'Title': 'Title Two', 'Author': 'Author Two', 'Pages': 200, 'Rating': 4.0, 'Genre': 'Non-Fiction'},
    {'Title': 'Title Three', 'Author': 'Author Three', 'Pages': 300, 'Rating': 4.8, 'Genre': 'Science Fiction'},
    {'Title': 'Title Four', 'Author': 'Author Four', 'Pages': 250, 'Rating': 3.9, 'Genre': 'Fantasy'},
    {'Title': 'Title Five', 'Author': 'Author Five', 'Pages': 180, 'Rating': 4.2, 'Genre': 'Mystery'},
]

@app.get("/books")
async def read_all_books():
    return BOOKS