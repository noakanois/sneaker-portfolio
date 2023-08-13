from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_id = request.headers.get("X-User-ID")  # or request.cookies.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID header missing")
        request.state.user_id = user_id
        return await call_next(request)

app.middleware("http")(UserIDMiddleware)
