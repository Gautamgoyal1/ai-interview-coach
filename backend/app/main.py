from app.modules.auth.router import router as auth_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.resume.router import router as resume_router

app = FastAPI(title="AI Interview Coach")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(resume_router)
app.include_router(auth_router)
app.include_router(resume_router)

@app.get("/health")
def health():
    return {"status": "ok"}
