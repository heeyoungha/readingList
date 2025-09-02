"""
페르소나 시스템 FastAPI 백엔드
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from loguru import logger

from models.persona_generator import PersonaGenerator
from utils.text_preprocessor import TextPreprocessor
from utils.emotion_analyzer import EmotionAnalyzer
from utils.topic_analyzer import TopicAnalyzer
from utils.embedding_generator import EmbeddingGenerator
from utils.vector_database import VectorDatabase
from config import settings

# FastAPI 앱 생성
app = FastAPI(
    title="페르소나 시스템 API",
    description="북클럽 데이터를 활용한 개인 맞춤형 페르소나 시스템",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경용, 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 인스턴스
persona_generator = PersonaGenerator()
text_preprocessor = TextPreprocessor()
emotion_analyzer = EmotionAnalyzer()
topic_analyzer = TopicAnalyzer()
embedding_generator = EmbeddingGenerator()
vector_database = VectorDatabase()

# Pydantic 모델
class UserData(BaseModel):
    id: str
    name: str
    books: Optional[List[Dict[str, Any]]] = []
    action_lists: Optional[List[Dict[str, Any]]] = []
    notes: Optional[List[Dict[str, Any]]] = []


class TextAnalysisRequest(BaseModel):
    text: str
    analysis_type: str = "all"  # "preprocessing", "emotion", "topic", "all"


class PersonaRequest(BaseModel):
    user_data: UserData


class EmbeddingRequest(BaseModel):
    texts: List[str]
    save_path: Optional[str] = None


class VectorSearchRequest(BaseModel):
    query_text: str
    k: int = 5


class AnalysisResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str


# 헬스체크 엔드포인트
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "페르소나 시스템 API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }


# 텍스트 분석 엔드포인트
@app.post("/analyze/text", response_model=AnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """텍스트 분석 API"""
    try:
        text = request.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="텍스트가 비어있습니다.")
        
        result = {}
        
        if request.analysis_type in ["preprocessing", "all"]:
            # 텍스트 전처리
            result["preprocessing"] = text_preprocessor.preprocess_text(text)
            result["writing_style"] = text_preprocessor.analyze_writing_style(text)
        
        if request.analysis_type in ["emotion", "all"]:
            # 감정 분석
            result["emotion"] = emotion_analyzer.get_emotion_summary(text)
        
        if request.analysis_type in ["topic", "all"]:
            # 토픽 분석
            result["topic"] = topic_analyzer.get_topic_summary([text])
        
        return AnalysisResponse(
            success=True,
            data=result,
            message="텍스트 분석이 완료되었습니다."
        )
        
    except Exception as e:
        logger.error(f"텍스트 분석 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"텍스트 분석 중 오류가 발생했습니다: {str(e)}")


# 페르소나 생성 엔드포인트
@app.post("/persona/generate", response_model=AnalysisResponse)
async def generate_persona(request: PersonaRequest):
    """페르소나 생성 API"""
    try:
        user_data = request.user_data.dict()
        
        # 페르소나 생성
        persona = persona_generator.generate_persona(user_data)
        
        return AnalysisResponse(
            success=True,
            data=persona,
            message="페르소나가 성공적으로 생성되었습니다."
        )
        
    except Exception as e:
        logger.error(f"페르소나 생성 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"페르소나 생성 중 오류가 발생했습니다: {str(e)}")


# Phase 2: 임베딩 생성 엔드포인트
@app.post("/embeddings/generate", response_model=AnalysisResponse)
async def generate_embeddings(request: EmbeddingRequest):
    """텍스트 임베딩 생성 API"""
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="텍스트 목록이 비어있습니다.")
        
        # 임베딩 생성
        embeddings_data = embedding_generator.generate_embeddings(request.texts)
        
        # 저장 경로가 지정된 경우 저장
        if request.save_path:
            embedding_generator.save_embeddings(embeddings_data, request.save_path)
        
        # 통계 정보 추가
        stats = embedding_generator.get_embedding_stats(embeddings_data)
        embeddings_data['stats'] = stats
        
        return AnalysisResponse(
            success=True,
            data=embeddings_data,
            message="임베딩이 성공적으로 생성되었습니다."
        )
        
    except Exception as e:
        logger.error(f"임베딩 생성 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"임베딩 생성 중 오류가 발생했습니다: {str(e)}")


# 사용자 데이터 임베딩 생성 엔드포인트
@app.post("/embeddings/user", response_model=AnalysisResponse)
async def generate_user_embeddings(request: PersonaRequest):
    """사용자 데이터 임베딩 생성 API"""
    try:
        user_data = request.user_data.dict()
        
        # 사용자 데이터 임베딩 생성
        user_embeddings = embedding_generator.generate_user_embeddings(user_data)
        
        if user_embeddings['chunks']:
            # 자동 저장
            save_path = f"./data/processed/user_{user_data['id']}_embeddings"
            embedding_generator.save_embeddings(user_embeddings, save_path)
            
            # 통계 정보 추가
            stats = embedding_generator.get_embedding_stats(user_embeddings)
            user_embeddings['stats'] = stats
            
            return AnalysisResponse(
                success=True,
                data=user_embeddings,
                message="사용자 데이터 임베딩이 성공적으로 생성되었습니다."
            )
        else:
            return AnalysisResponse(
                success=True,
                data=user_embeddings,
                message="처리할 텍스트가 없습니다."
            )
        
    except Exception as e:
        logger.error(f"사용자 데이터 임베딩 생성 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"사용자 데이터 임베딩 생성 중 오류가 발생했습니다: {str(e)}")


# 벡터 데이터베이스 인덱스 생성 엔드포인트
@app.post("/vector-db/create", response_model=AnalysisResponse)
async def create_vector_index(embedding_dim: int, index_type: str = "IVFFlat"):
    """FAISS 벡터 인덱스 생성 API"""
    try:
        vector_database.create_index(embedding_dim, index_type)
        
        stats = vector_database.get_index_stats()
        
        return AnalysisResponse(
            success=True,
            data=stats,
            message="벡터 인덱스가 성공적으로 생성되었습니다."
        )
        
    except Exception as e:
        logger.error(f"벡터 인덱스 생성 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"벡터 인덱스 생성 중 오류가 발생했습니다: {str(e)}")


# 벡터 검색 엔드포인트
@app.post("/vector-db/search", response_model=AnalysisResponse)
async def search_vectors(request: VectorSearchRequest):
    """벡터 검색 API"""
    try:
        if not vector_database.index:
            raise HTTPException(status_code=400, detail="벡터 인덱스가 생성되지 않았습니다.")
        
        # 텍스트로 검색
        results = vector_database.search_by_text(
            query_text=request.query_text,
            k=request.k,
            embedding_generator=embedding_generator
        )
        
        return AnalysisResponse(
            success=True,
            data={
                "query": request.query_text,
                "results": results,
                "total_results": len(results)
            },
            message="벡터 검색이 완료되었습니다."
        )
        
    except Exception as e:
        logger.error(f"벡터 검색 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"벡터 검색 중 오류가 발생했습니다: {str(e)}")


# 벡터 데이터베이스 통계 엔드포인트
@app.get("/vector-db/stats")
async def get_vector_db_stats():
    """벡터 데이터베이스 통계 정보 API"""
    try:
        stats = vector_database.get_index_stats()
        return {
            "success": True,
            "data": stats,
            "message": "벡터 데이터베이스 통계 정보를 반환합니다."
        }
        
    except Exception as e:
        logger.error(f"벡터 DB 통계 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"벡터 DB 통계 조회 중 오류가 발생했습니다: {str(e)}")


# 배치 분석 엔드포인트
@app.post("/analyze/batch", response_model=AnalysisResponse)
async def analyze_batch_texts(texts: List[str]):
    """여러 텍스트 배치 분석 API"""
    try:
        if not texts:
            raise HTTPException(status_code=400, detail="텍스트 목록이 비어있습니다.")
        
        # 텍스트 전처리
        processed_texts = []
        for text in texts:
            if text and text.strip():
                processed = text_preprocessor.preprocess_text(text.strip())
                processed_texts.append(processed)
        
        # 감정 분석
        emotion_analysis = emotion_analyzer.analyze_multiple_texts(texts)
        
        # 토픽 분석
        topic_analysis = topic_analyzer.get_topic_summary(texts)
        
        result = {
            "processed_texts": processed_texts,
            "emotion_analysis": emotion_analysis,
            "topic_analysis": topic_analysis,
            "total_texts": len([t for t in texts if t and t.strip()])
        }
        
        return AnalysisResponse(
            success=True,
            data=result,
            message="배치 분석이 완료되었습니다."
        )
        
    except Exception as e:
        logger.error(f"배치 분석 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"배치 분석 중 오류가 발생했습니다: {str(e)}")


# 설정 정보 엔드포인트
@app.get("/config")
async def get_config():
    """시스템 설정 정보 반환"""
    return {
        "embedding_model": settings.embedding_model,
        "chunk_size": settings.chunk_size,
        "max_tokens": settings.max_tokens,
        "vector_db_path": settings.vector_db_path,
        "data_path": settings.data_path
    }


# 에러 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 핸들러"""
    logger.error(f"전역 예외 발생: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "내부 서버 오류가 발생했습니다.",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    # 개발 서버 실행
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 