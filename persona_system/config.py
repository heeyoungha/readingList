"""
페르소나 시스템 설정 파일
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # OpenAI API 설정
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    
    # Supabase 설정
    supabase_url: str = ""
    supabase_anon_key: str = ""
    
    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # 모델 설정
    embedding_model: str = "jhgan/ko-sroberta-multitask"
    chunk_size: int = 512
    max_tokens: int = 1000
    
    # 데이터베이스 설정
    vector_db_path: str = "./data/faiss_index"
    data_path: str = "./data/processed"
    
    # 로깅 설정
    log_level: str = "INFO"
    log_file: str = "./logs/persona_system.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()


def get_openai_api_key() -> Optional[str]:
    """OpenAI API 키 반환"""
    return settings.openai_api_key or os.getenv("OPENAI_API_KEY")


def get_supabase_config() -> tuple[str, str]:
    """Supabase 설정 반환"""
    url = settings.supabase_url or os.getenv("SUPABASE_URL", "")
    key = settings.supabase_anon_key or os.getenv("SUPABASE_ANON_KEY", "")
    return url, key 