from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Création de l'objet FastAPI
app = FastAPI()

# Endpoint de test : /
@app.get("/")
async def root():
    return JSONResponse(content={"message": "🚀 Movie recommender backend is running!"})
