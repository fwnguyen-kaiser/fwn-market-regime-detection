import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
import sys

app = FastAPI(title="Market Regime Detection API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👇 SỬA LẠI MIDDLEWARE - Dùng print với sys.stdout.flush()
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"🔥 [INCOMING] {request.method} {request.url}")
    sys.stdout.flush()  # 👈 FORCE FLUSH
    response = await call_next(request)
    print(f"✅ [DONE] {response.status_code}")
    sys.stdout.flush()
    return response

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    print("📍 Root endpoint hit!")
    sys.stdout.flush()
    return {"message": "Server is UP"}