from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()

model = joblib.load("models/best_model.pkl")

@app.get("/")
def home():
    return {"message": "AI Shopping Planner API"}

@app.post("/predict")
def predict(features: list):
    prediction = model.predict([features])
    return {"prediction": prediction.tolist()}