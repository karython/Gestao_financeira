# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Gestão Financeira API"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'mysql+aiomysql://u275872813_gen_financas:Karython0705@195.179.238.1:3306/u275872813_gen_financas')
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "https://karython.github.io", "http://127.0.0.1:5500", "http://127.0.0.1:5500", "https://gestao-financeira-tmqc.onrender.com", "null"]
    
    # Email (para relatórios)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@financeiro.com"
    
    class Config:
        env_file = ".env"


settings = Settings()

