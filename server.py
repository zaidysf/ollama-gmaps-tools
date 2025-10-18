"""Google Maps Place Search Tool for OpenWebUI"""
import os
import re
from datetime import datetime, timedelta
from collections import deque
from typing import Optional, List
import requests
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
TOOL_API_KEY = os.getenv("TOOL_API_KEY", "heypico_maps_secret_2024")
PORT = int(os.getenv("SERVER_PORT", "9000"))
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

if not GOOGLE_MAPS_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY is required")

app = FastAPI(
    title="Google Maps Search",
    description="Search places using natural language",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

class RateLimiter:
    def __init__(self, max_per_min: int):
        self.max = max_per_min
        self.requests = deque()

    def check(self) -> bool:
        now = datetime.now()
        while self.requests and self.requests[0] < now - timedelta(minutes=1):
            self.requests.popleft()
        if len(self.requests) < self.max:
            self.requests.append(now)
            return True
        return False

limiter = RateLimiter(RATE_LIMIT)

def verify_token(creds: HTTPAuthorizationCredentials = Security(security)):
    if creds.credentials != TOOL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid token")
    return creds.credentials

class SearchRequest(BaseModel):
    query: str

class Place(BaseModel):
    name: str
    address: str
    rating: Optional[float] = None
    latitude: float
    longitude: float
    maps_url: str
    directions_url: str

class SearchResponse(BaseModel):
    success: bool
    query: str
    location_found: Optional[str] = None
    count: int
    places: List[Place]
    display_message: str

def extract_location(query: str) -> tuple[str, Optional[str]]:
    patterns = [
        r'\b(?:in|at)\s+(.+)$',
        r'\b(?:near|around)\s+(.+)$',
        r'^.+?\s+(?:in|at|near|around)\s+(.+)$',
    ]

    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            search = re.sub(pattern, '', query, flags=re.IGNORECASE).strip()
            search = re.sub(r'^(find|show|get|look for|where|what)\s+', '', search, flags=re.IGNORECASE).strip()
            return (search, location)

    return (query, None)

@app.post("/search_places", response_model=SearchResponse)
async def search_places(request: SearchRequest, token: str = Depends(verify_token)):
    if not limiter.check():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    search_term, location = extract_location(request.query)

    if location:
        google_query = f"{search_term} in {location}"
    else:
        google_query = search_term

    try:
        response = requests.get(
            "https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={"query": google_query, "key": GOOGLE_MAPS_API_KEY},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK":
            if data.get("status") == "ZERO_RESULTS":
                return SearchResponse(
                    success=False,
                    query=request.query,
                    location_found=location,
                    count=0,
                    places=[],
                    display_message=f"No places found for '{request.query}'. Try a different search."
                )
            raise Exception(f"Google API error: {data.get('status')}")

        results = data.get("results", [])[:5]

        places = []
        for r in results:
            lat = r["geometry"]["location"]["lat"]
            lng = r["geometry"]["location"]["lng"]
            pid = r.get("place_id", "")

            places.append(Place(
                name=r.get("name", "Unknown"),
                address=r.get("formatted_address", "No address"),
                rating=r.get("rating"),
                latitude=lat,
                longitude=lng,
                maps_url=f"https://www.google.com/maps/place/?q=place_id:{pid}" if pid else f"https://www.google.com/maps/search/?api=1&query={lat},{lng}",
                directions_url=f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
            ))

        loc_text = f" in {location}" if location else ""
        msg_lines = [f"Found {len(places)} places{loc_text}:\n"]

        for i, place in enumerate(places, 1):
            rating_stars = "⭐" * int(place.rating) if place.rating else "No rating"
            msg_lines.append(f"\n{i}. **{place.name}**")
            msg_lines.append(f"   Rating: {place.rating or 'N/A'} {rating_stars}")
            msg_lines.append(f"   Address: {place.address}")
            msg_lines.append(f"   [📍 View on Google Maps]({place.maps_url})")
            msg_lines.append(f"   [🚗 Get Directions]({place.directions_url})")

        return SearchResponse(
            success=True,
            query=request.query,
            location_found=location,
            count=len(places),
            places=places,
            display_message="\n".join(msg_lines)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🚀 Google Maps Search Tool")
    print(f"📍 http://0.0.0.0:{PORT}")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
