from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import os

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# create app
app = FastAPI()

# CORS (frontend connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# base path
BASE_DIR = os.path.dirname(__file__)

# load model
model = pickle.load(open(os.path.join(BASE_DIR, "model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join(BASE_DIR, "vectorizer.pkl"), "rb"))

# static folder ONLY
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

# serve frontend
@app.get("/")
def serve_home():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

# request model
class News(BaseModel):
    text: str

# prediction API
@app.post("/predict")
def predict(news: News):
    data = vectorizer.transform([news.text])
    prediction = model.predict(data)[0]
    confidence = model.predict_proba(data).max()

    return {
        "prediction": str(prediction),   # ensure string
        "confidence": float(confidence)
    }
