from fastapi import FastAPI
from Routers import RegUser, Auth, GetMe, TenderAnalysis, UserDocuments
import os
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


app = FastAPI()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

app.include_router(RegUser.router)
app.include_router(Auth.router)
app.include_router(GetMe.router)
app.include_router(TenderAnalysis.router)
app.include_router(UserDocuments.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],   
)


@app.get("/")
def root():
    return {"message": "Hello World"}
