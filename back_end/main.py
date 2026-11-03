import os
import time

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import models
from database import create_tables
from seed import seed
from services_api import router as services_router

load_dotenv()

create_tables()
seed()  # fills an empty database (e.g. the first deploy); does nothing once services exist

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACE_ID = os.getenv("GOOGLE_PLACE_ID")

CACHE_TTL_SECONDS = 60 * 60 * 24  # refresh once a day

# Websites allowed to call this API, comma separated. Online, set FRONTEND_ORIGINS
# to the website's address, e.g. "https://rosa-nails.vercel.app".
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app = FastAPI(title="Rosa Nails & Spa API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(services_router)

_cache: dict = {"payload": None, "fetched_at": 0.0}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/reviews")
async def get_reviews():
    now = time.time()

    cached = _cache["payload"]
    if cached is not None and now - _cache["fetched_at"] < CACHE_TTL_SECONDS:
        return cached

    if not API_KEY or not PLACE_ID:
        raise HTTPException(
            status_code=500,
            detail="Google Places credentials are not configured",
        )

    url = f"https://places.googleapis.com/v1/places/{PLACE_ID}"
    headers = {
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "rating,userRatingCount,reviews",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        if cached is not None:
            return cached
        raise HTTPException(
            status_code=502,
            detail=f"Google Places error {response.status_code}: {response.text[:300]}",
        )

    data = response.json()

    payload = {
        "summary": {
            "rating": data.get("rating", 0),
            "total": data.get("userRatingCount", 0),
        },
        "reviews": [
            {
                "id": review.get("name", f"review-{index}"),
                "author": review.get("authorAttribution", {}).get(
                    "displayName", "Anonymous"
                ),
                "rating": review.get("rating", 5),
                "text": review.get("text", {}).get("text", ""),
                "relativeTime": review.get("relativePublishTimeDescription", ""),
            }
            for index, review in enumerate(data.get("reviews", []))
        ],
    }

    _cache["payload"] = payload
    _cache["fetched_at"] = now
    return payload