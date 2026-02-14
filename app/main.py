from fastapi import FastAPI
from app.routes import items

app = FastAPI()

app.include_router(items.router)

@app.get("/")
async def root():
    return {"message": "Welcome!"}