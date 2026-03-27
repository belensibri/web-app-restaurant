from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, menu, orders, ws

app = FastAPI(title="TableFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:5005", "http://fe:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(ws.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
