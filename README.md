# Google Maps LLM Integration for HeyPico.ai

**Author:** Zaid Yasyaf
**Email:** zaid.ug@gmail.com
**Date:** October 2025
**Assessment:** HeyPico.ai Technical Test

---

## 📋 Project Requirements

This project fulfills the HeyPico.ai code test requirements:

> Run your own local LLM that can output google maps's map when the user prompts the LLM where to find places to go/eat/etc. User should be able to view the location direction on the embedded map or open a link to view.

**Requirements Met:**
- ✅ Local LLM (Ollama with OpenWebUI)
- ✅ Google Maps integration with clickable links and directions
- ✅ Backend API in Python (FastAPI)
- ✅ Best practices for Google Maps API (security, rate limiting, error handling)
- ✅ New Google Cloud account with free credits
- ✅ Clean, production-ready code

---

## 🎯 Working Demo

![Working Demo](OpenWebUI%20-%20HeyPico.png)

*Screenshot shows the system successfully finding coffee shops in Karawaci, Banten, Indonesia with clickable Google Maps links and directions.*

---

## 🚀 Features

- **Natural Language Processing**: Automatically extracts locations from user queries
- **Google Maps Integration**: Returns top 5 places with ratings, addresses, and locations
- **Clickable Links**: Direct Google Maps links and turn-by-turn directions for each result
- **Secure API**: Bearer token authentication and API key protection
- **Rate Limiting**: 60 requests/minute to protect Google Maps quota
- **Simple Architecture**: Single-parameter API design for reliability
- **Production Ready**: Clean code, error handling, comprehensive documentation

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11 with FastAPI
- **LLM**: Ollama (llama3.3) running locally
- **UI**: OpenWebUI v0.6.34
- **API**: Google Maps Places API
- **Security**: Environment variables, Bearer token auth, rate limiting

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- OpenWebUI installed and running
- Google Maps API key (free $200 credit available)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd heypico
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
SERVER_HOST=0.0.0.0
SERVER_PORT=9000
TOOL_API_KEY=your_secret_token_here
RATE_LIMIT_PER_MINUTE=60
```

4. **Start the server**
```bash
python server.py
```

Server runs on: http://localhost:9000

---

## 🔌 Connect to OpenWebUI

1. Open OpenWebUI: http://localhost:8080
2. Navigate to **Settings** → **External Tools**
3. Click **"+ Add Connection"**
4. Configure the connection:
   - **API Base URL:** `http://localhost:9000`
   - **OpenAPI Spec:** Select "URL", enter: `openapi.json`
   - **Auth Type:** Select "Bearer"
   - **API Key:** `heypico_maps_secret_2024` (or your custom token from .env)
5. Click **Save**
6. Start a **new chat**
7. Test with: `Find coffee shops in Karawaci, Banten, Indonesia`

---

## 💡 Usage Examples

The system understands natural language queries. Simply ask:

```
"Find coffee shops in Karawaci, Banten, Indonesia"
"Show me Italian restaurants near Jakarta"
"What are the best gyms around Singapore?"
"Tourist attractions in Bali"
"Pizza places near Tangerang"
```

**Response Format:**
- Place name with star ratings
- Full address
- Clickable "View on Google Maps" link
- Clickable "Get Directions" link

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   OpenWebUI (Port 8080)             │
│   - User Interface                  │
│   - Ollama LLM (llama3.3)           │
└──────────────┬──────────────────────┘
               │
               │ HTTP REST API
               │ Bearer Token Auth
               │
┌──────────────▼──────────────────────┐
│   FastAPI Server (Port 9000)        │
│   - Natural language processing     │
│   - Location extraction             │
│   - Rate limiting                   │
│   - Authentication                  │
└──────────────┬──────────────────────┘
               │
               │ HTTPS
               │ API Key
               │
┌──────────────▼──────────────────────┐
│   Google Maps Platform              │
│   - Places API (Text Search)        │
└─────────────────────────────────────┘
```

---

## 🔒 Security Implementation

### API Key Protection
- Google Maps API key stored in `.env` file
- Never committed to version control
- `.env` included in `.gitignore`

### Authentication
- Bearer token required for all API endpoints
- Configurable token in environment variables
- 401 Unauthorized for invalid tokens

### Rate Limiting
- Token bucket algorithm
- Default: 60 requests per minute
- Prevents API quota exhaustion
- Returns 429 status when limit exceeded

### Input Validation
- Pydantic models for request validation
- Automatic type checking
- Error handling for malformed requests

---

## 🧪 API Endpoints

### POST /search_places
Search for places using natural language.

**Request:**
```json
{
  "query": "coffee shops in Karawaci, Banten, Indonesia"
}
```

**Response:**
```json
{
  "success": true,
  "query": "coffee shops in Karawaci, Banten, Indonesia",
  "location_found": "Karawaci, Banten, Indonesia",
  "count": 5,
  "places": [
    {
      "name": "TITIK NYEDUH COFFEE ROASTER",
      "address": "Jl. Aria Santika No.47...",
      "rating": 4.6,
      "latitude": -6.1784,
      "longitude": 106.6169126,
      "maps_url": "https://www.google.com/maps/place/?q=place_id:...",
      "directions_url": "https://www.google.com/maps/dir/?api=1&destination=..."
    }
  ],
  "display_message": "Found 5 places in Karawaci..."
}
```

### GET /health
Health check endpoint (no authentication required).

**Response:**
```json
{
  "status": "ok"
}
```

---

## 📊 Key Assumptions

1. **Single Parameter Design**: Used one `query` parameter instead of multiple fields for better LLM reliability
2. **Rate Limiting**: Set at 60 requests/minute to stay within free tier limits
3. **Result Limit**: Returns top 5 results for optimal user experience
4. **Location Extraction**: Uses regex patterns to extract locations from natural language
5. **Link-Based Maps**: Provides clickable links instead of embedded iframes for better compatibility with OpenWebUI

---

## 📁 Project Structure

```
heypico/
├── server.py              # FastAPI backend server (182 lines)
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration (not in git)
├── .env.example           # Template for environment setup
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── OpenWebUI - HeyPico.png # Working demo screenshot
```

---

## 🧑‍💻 Development

### Requirements

All dependencies listed in `requirements.txt`:
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
python-dotenv>=1.0.0
requests>=2.32.0
```

### Code Quality
- Clean, commented code
- Type hints throughout
- Comprehensive error handling
- Production-ready structure

---

## 🎯 How It Works

1. **User Query**: User asks LLM in natural language (e.g., "Find coffee in Karawaci")
2. **LLM Detection**: OpenWebUI's LLM detects the need to search for places
3. **API Call**: LLM calls `/search_places` endpoint with the query
4. **Location Extraction**: Server extracts "Karawaci" from the query using regex
5. **Google API**: Queries Google Places API for "coffee in Karawaci"
6. **Response Format**: Formats results with ratings, addresses, and clickable links
7. **User Display**: LLM shows formatted results to user with working links

---

## ✅ Requirements Compliance

| Requirement | Implementation | Status |
|------------|----------------|---------|
| Local LLM | Ollama with OpenWebUI | ✅ |
| Google Maps output | Clickable links with directions | ✅ |
| View directions | Google Maps links per result | ✅ |
| Python/JS backend | FastAPI (Python) | ✅ |
| Best practices | Security, rate limiting, error handling | ✅ |
| Google Cloud account | New account with $200 credit | ✅ |
| OpenWebUI usage | External Tools integration | ✅ |
| Popular LLM | Ollama (llama3.3) | ✅ |
| AI-assisted coding | Disclosed and documented | ✅ |
| Assumptions explained | Listed in this README | ✅ |

---

## 📞 Contact

**Zaid Yasyaf**
Email: zaid.ug@gmail.com
GitHub: [Your GitHub Profile]

---

## 📄 License

This project was created as part of the HeyPico.ai technical assessment.

---

**Last Updated:** October 2025
**Server:** http://localhost:9000
**OpenWebUI:** http://localhost:8080
