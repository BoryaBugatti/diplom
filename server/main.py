from fastapi import FastAPI
from Routers import RegUser, Auth, GetMe, TenderAnalysis
import os
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = "../LLM/qwen2.5-tender-lora-3060/checkpoint-9"  
    base_model_name = "Qwen/Qwen2.5-3B-Instruct"
    
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True
    )
    
    from peft import PeftModel
    model = PeftModel.from_pretrained(model, model_path)
    model.eval()
    
    app.state.model = model
    app.state.tokenizer = tokenizer
    
    yield
    
    del app.state.model
    del app.state.tokenizer
    if torch.cuda.is_available():
        torch.cuda.empty_cache()



app = FastAPI(lifespan=lifespan)

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

app.include_router(RegUser.router)
app.include_router(Auth.router)
app.include_router(GetMe.router)
app.include_router(TenderAnalysis.router)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session_id",
    max_age=3600 * 24 * 7,
    same_site="lax",
    https_only=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],   
)


@app.get("/")
def root():
    return {"message": "Hello World"}
