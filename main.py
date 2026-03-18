from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from datetime import datetime, timezone
import logging

from security import verify_api_key
from validators import validate_sector
from analysis_service import fetch_market_data, generate_analysis, build_markdown


app = FastAPI(title="Trade Opportunities API")

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Logging
logging.basicConfig(level=logging.INFO)

# In-memory usage tracking (per user)
usage_tracker = {}


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})


@app.get("/")
async def root():
    return {
        "message": "Trade Opportunities API",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/analyze/{sector}")
@limiter.limit("5/minute")
async def analyze_sector(
    sector: str,
    request: Request,
    user=Depends(verify_api_key)
):
    """
    Analyze a sector and return a structured markdown report.
    """
    try:
        sector = validate_sector(sector)

        client_host = request.client.host if request.client else "unknown"
        user_id = user or client_host

        logging.info(f"Request from {user_id} for sector: {sector}")

        if user_id not in usage_tracker:
            usage_tracker[user_id] = 0
        usage_tracker[user_id] += 1

        data = await fetch_market_data(sector)
        analysis = await generate_analysis(sector, data)
        report = build_markdown(sector, analysis or "No analysis available")

        return {
            "sector": sector,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "usage_count": usage_tracker[user_id],
            "report": report
        }

    except Exception as e:
        logging.error(f"Error analyzing sector {sector}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )