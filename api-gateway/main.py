from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import httpx
import os

app = FastAPI(title="API Gateway FoodHub", description="Gateway untuk meneruskan request ke microservices", version="1.0.0")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://menu-service:8002")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8003")

async def forward_request(request: Request, service_url: str):
    path = request.url.path
    url = f"{service_url}{path}"
    
    headers = dict(request.headers)
    headers.pop("host", None) # Remove host header so httpx uses the correct one

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
@app.api_route("/menus/{menu_id}", methods=["GET", "DELETE"])
async def route_menu(request: Request):
    return await forward_request(request, MENU_SERVICE_URL)

# Routes for Order Service
@app.api_route("/orders", methods=["GET", "POST"])
@app.api_route("/orders/{order_id}", methods=["GET"])
@app.api_route("/orders/{order_id}/status", methods=["PUT"])
async def route_order(request: Request):
    return await forward_request(request, ORDER_SERVICE_URL)
