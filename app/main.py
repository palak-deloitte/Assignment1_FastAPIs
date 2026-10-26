import logging
from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel

from . import services, config
from .auth import verify_api_key

app = FastAPI(title="Assignment 1")

class WeatherResponse(BaseModel):
    city: str
    temperature: float
    condition: str
    humidity: int

class JokeResponseModel(BaseModel):
    joke: str
    category: str

class SummaryRequest(BaseModel):
    text: str = ""

class SummaryResponse(BaseModel):
    summary: str


@app.get("/weather", response_model=WeatherResponse)
def get_weather(city: str = Query(..., min_length=1)):
    try:
        return services.fetch_weather(city)
    except services.CityNotFound:
        raise HTTPException(status_code=404, detail=f"City '{city} not found")
    except services.UpstreamError:
        raise HTTPException(status_code=502, detail="Weather service unavailable")


@app.get("/joke", response_model=JokeResponseModel)
def get_joke():
    try:
        return services.fetch_joke()
    except services.UpstreamError:
        raise HTTPException(status_code=502, detail="Joke service unavailable")

@app.post("/summary", response_model=SummaryResponse, dependencies=[Depends(verify_api_key)])
def post_summary(body: SummaryRequest):
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="'text' should not be empty")
    if len(text) > config.MAX_TEXT_LENGTH:
        raise HTTPException(status_code=400, detail="'text' exceeds maximum length of {config.MAX_TEXT_LENGTH} characters")

    try:
        return {"summary": services.summarize_text(text)}
    except services.UpstreamError:
        raise HTTPException(status_code=502, detail="Summary service unavailable")