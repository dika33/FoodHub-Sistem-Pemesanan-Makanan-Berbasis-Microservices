from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Gateway FoodHub", description="Gateway untuk meneruskan request ke microservices", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://menu-service:8002")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8003")

async def validate_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token tidak ditemukan atau tidak valid")
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{USER_SERVICE_URL}/users/me", headers={"Authorization": auth_header})
            if res.status_code != 200:
                raise HTTPException(status_code=401, detail="Token kadaluarsa atau tidak valid")
            return res.json()
        except Exception:
            raise HTTPException(status_code=503, detail="User Service tidak tersedia")

async def forward_request(request: Request, service_url: str):
    path = request.url.path
    url = f"{service_url}{path}"
    
    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()

    async with httpx.AsyncClient() as client:
        try:
            req = client.build_request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            response = await client.send(req)
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.RequestError as exc:
            return JSONResponse(status_code=503, content={"detail": f"Service unavailable: {exc}"})

# Routes for User Service
@app.api_route("/register", methods=["POST"])
@app.api_route("/login", methods=["POST"])
@app.api_route("/users/me", methods=["GET"])
async def route_user(request: Request):
    return await forward_request(request, USER_SERVICE_URL)

# Routes for Menu Service
@app.api_route("/categories", methods=["GET", "POST"])
@app.api_route("/categories/{category_id}", methods=["GET", "DELETE"])
@app.api_route("/menus", methods=["GET", "POST"])
@app.api_route("/menus/{menu_id}", methods=["GET", "DELETE", "PUT"])
async def route_menu(request: Request):
    if request.method != "GET":
        # Proteksi rute write (POST, PUT, DELETE) khusus ADMIN
        user = await validate_token(request)
        if user.get("username", "").lower() != "admin":
            raise HTTPException(status_code=403, detail="Akses ditolak: Hanya Admin yang bisa mengelola menu")
    return await forward_request(request, MENU_SERVICE_URL)

# Routes for Order Service
@app.api_route("/orders", methods=["GET", "POST"])
@app.api_route("/orders/{order_id}", methods=["GET"])
@app.api_route("/orders/{order_id}/status", methods=["PUT"])
async def route_order(request: Request):
    if request.method != "GET":
        # Wajibkan login untuk membuat pesanan
        await validate_token(request)
    return await forward_request(request, ORDER_SERVICE_URL)
