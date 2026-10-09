
import os
import time
import uuid
import math

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse, Response

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-bnhqj7.example.com"
EMAIL = "23f2004539@ds.study.iitm.ac.in"


@app.middleware("http")
async def request_headers_and_cors(request: Request, call_next):
    start = time.perf_counter()
    origin = request.headers.get("origin")

    if request.method == "OPTIONS" and request.url.path == "/stats":
        if origin == ALLOWED_ORIGIN:
            response = Response(status_code=204)
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Vary"] = "Origin"
        else:
            response = Response(status_code=403)
    else:
        response = await call_next(request)

        if origin == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Vary"] = "Origin"

    response.headers["X-Request-ID"] = str(uuid.uuid4())
    elapsed = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{elapsed:.6f}"

    return response


@app.get("/")
def home():
    return {"service": "CORS-aware metrics API", "status": "ok"}


@app.get("/stats")
def stats(values: str = Query(...)):
    try:
        numbers = [int(item.strip()) for item in values.split(",")]

        if not numbers or any(not item.strip() for item in values.split(",")):
            raise ValueError("Empty value")

    except (ValueError, TypeError):
        return JSONResponse(
            status_code=400,
            content={"error": "values must be comma-separated integers"},
        )

    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": sum(numbers) / len(numbers),
    }

