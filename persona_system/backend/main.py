"""
🚀 Phase 5: 사용자 인터페이스 및 테스트

FastAPI 백엔드 서버 - 페르소나 챗봇 API 및 웹 인터페이스
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
import uvicorn

from utils import PersonaChatbot, SearchSystem
from config import settings


# FastAPI 앱 초기화
app = FastAPI(
    title="🤖 페르소나 챗봇 API",
    description="개인 맞춤형 프로젝트 추천 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
static_path = project_root / "static"
templates_path = project_root / "templates"

# 디렉토리 생성
static_path.mkdir(exist_ok=True)
templates_path.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
templates = Jinja2Templates(directory=str(templates_path))

# 전역 챗봇 인스턴스 (싱글톤)
chatbot: Optional[PersonaChatbot] = None
user_sessions: Dict[str, PersonaChatbot] = {}


# Pydantic 모델들
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    use_search: bool = True
    search_k: int = 5


class PersonaAnalysisRequest(BaseModel):
    user_data: List[Dict[str, Any]]
    session_id: Optional[str] = "default"


class FeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    rating: int  # 1-5
    feedback: Optional[str] = ""


class ChatResponse(BaseModel):
    success: bool
    response: str
    session_id: str
    metadata: Dict[str, Any]
    error: Optional[str] = None


def get_chatbot(session_id: str = "default") -> PersonaChatbot:
    """세션별 챗봇 인스턴스 반환 (싱글톤 패턴)"""
    global user_sessions
    
    if session_id not in user_sessions:
        user_sessions[session_id] = PersonaChatbot()
        logger.info(f"🤖 새 챗봇 세션 생성: {session_id}")
    
    return user_sessions[session_id]


@app.on_event("startup")
async def startup_event():
    """서버 시작시 초기화"""
    logger.info("🚀 Phase 5 페르소나 챗봇 서버 시작")
    
    # 기본 챗봇 인스턴스 생성
    global chatbot
    chatbot = PersonaChatbot()
    
    # 시스템 상태 확인
    status = chatbot.get_system_status()
    logger.info("📊 시스템 상태:")
    for key, value in status.items():
        logger.info(f"  - {key}: {value}")
    
    if not status.get('api_key_configured'):
        logger.warning("⚠️ OpenAI API 키가 설정되지 않았습니다. 일부 기능이 제한됩니다.")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """메인 웹 인터페이스"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/health")
async def health_check():
    """헬스체크 엔드포인트"""
    global chatbot
    if not chatbot:
        chatbot = PersonaChatbot()
    
    status = chatbot.get_system_status()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system_status": status
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatMessage):
    """채팅 API 엔드포인트"""
    try:
        session_chatbot = get_chatbot(chat_request.session_id)
        
        # 프로젝트 추천 생성
        result = session_chatbot.generate_project_recommendations(
            user_question=chat_request.message,
            search_k=chat_request.search_k,
            use_conversation_history=True
        )
        
        if result['success']:
            return ChatResponse(
                success=True,
                response=result['recommendation'],
                session_id=chat_request.session_id,
                metadata={
                    "tokens_used": result['metadata']['tokens_used'],
                    "search_count": result['metadata']['search_count'],
                    "prompt_type": result['prompt_type'],
                    "context_used": result['context_used'],
                    "timestamp": result['metadata']['timestamp']
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
            
    except Exception as e:
        logger.error(f"❌ 채팅 API 오류: {e}")
        return ChatResponse(
            success=False,
            response="죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.",
            session_id=chat_request.session_id,
            metadata={},
            error=str(e)
        )


@app.post("/api/persona-analysis")
async def analyze_persona(analysis_request: PersonaAnalysisRequest):
    """페르소나 분석 API 엔드포인트"""
    try:
        session_chatbot = get_chatbot(analysis_request.session_id)
        
        result = session_chatbot.analyze_user_persona(analysis_request.user_data)
        
        if result['success']:
            return {
                "success": True,
                "persona": result['persona'],
                "session_id": analysis_request.session_id,
                "metadata": result['metadata']
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
            
    except Exception as e:
        logger.error(f"❌ 페르소나 분석 API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-data")
async def upload_user_data(
    session_id: str = Form("default"),
    file: UploadFile = File(...)
):
    """사용자 데이터 업로드 (JSON 파일)"""
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="JSON 파일만 업로드 가능합니다.")
        
        content = await file.read()
        user_data = json.loads(content.decode('utf-8'))
        
        # 데이터 형식 검증
        if not isinstance(user_data, list):
            raise HTTPException(status_code=400, detail="데이터는 리스트 형태여야 합니다.")
        
        # 검색 시스템에 데이터 추가
        session_chatbot = get_chatbot(session_id)
        search_system = session_chatbot.search_system
        
        # 텍스트 추출
        texts = []
        metadata = []
        for i, item in enumerate(user_data):
            content = item.get('content', '')
            if content:
                texts.append(content)
                metadata.append({
                    'id': f'uploaded_{i}',
                    'type': item.get('type', 'user_data'),
                    'date': item.get('date', datetime.now().isoformat()),
                    **item
                })
        
        if texts:
            # 임베딩 생성 및 인덱스에 추가
            embedding_result = search_system.embedding_generator.generate_embeddings(texts)
            if isinstance(embedding_result, dict):
                embeddings = embedding_result['embeddings']
            else:
                embeddings = embedding_result
            
            # 기존 인덱스가 없다면 새로 생성
            if search_system.vector_db.index is None:
                search_system.vector_db.create_index(embeddings.shape[1], index_type="Flat")
            
            search_system.vector_db.add_vectors(embeddings, metadata)
            
            logger.info(f"📁 사용자 데이터 업로드 완료: {len(texts)}개 문서, 세션 {session_id}")
        
        return {
            "success": True,
            "message": f"{len(texts)}개 문서가 성공적으로 업로드되었습니다.",
            "session_id": session_id,
            "document_count": len(texts)
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="유효하지 않은 JSON 파일입니다.")
    except Exception as e:
        logger.error(f"❌ 파일 업로드 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feedback")
async def submit_feedback(feedback_request: FeedbackRequest):
    """사용자 피드백 제출"""
    try:
        # 피드백을 파일로 저장 (실제 서비스에서는 데이터베이스 사용)
        feedback_dir = project_root / "data" / "feedback"
        feedback_dir.mkdir(parents=True, exist_ok=True)
        
        feedback_data = {
            "session_id": feedback_request.session_id,
            "message_id": feedback_request.message_id,
            "rating": feedback_request.rating,
            "feedback": feedback_request.feedback,
            "timestamp": datetime.now().isoformat()
        }
        
        feedback_file = feedback_dir / f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📝 피드백 저장: {feedback_request.rating}/5, 세션 {feedback_request.session_id}")
        
        return {
            "success": True,
            "message": "피드백이 성공적으로 제출되었습니다.",
            "timestamp": feedback_data["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"❌ 피드백 제출 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}/history")
async def get_session_history(session_id: str):
    """세션 대화 히스토리 조회"""
    try:
        if session_id not in user_sessions:
            return {
                "success": True,
                "session_id": session_id,
                "history": [],
                "summary": {"total_exchanges": 0, "conversation_started": False}
            }
        
        session_chatbot = user_sessions[session_id]
        summary = session_chatbot.get_conversation_summary()
        
        return {
            "success": True,
            "session_id": session_id,
            "history": session_chatbot.conversation_history,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"❌ 히스토리 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """세션 초기화"""
    try:
        if session_id in user_sessions:
            user_sessions[session_id].clear_conversation_history()
            logger.info(f"🗑️ 세션 초기화: {session_id}")
        
        return {
            "success": True,
            "message": f"세션 {session_id}이 초기화되었습니다."
        }
        
    except Exception as e:
        logger.error(f"❌ 세션 초기화 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_system_stats():
    """시스템 통계"""
    try:
        stats = {
            "active_sessions": len(user_sessions),
            "session_ids": list(user_sessions.keys()),
            "total_conversations": sum(
                len(chatbot.conversation_history) // 2 
                for chatbot in user_sessions.values()
            ),
            "system_status": chatbot.get_system_status() if chatbot else {},
            "timestamp": datetime.now().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}/authors")
async def get_session_authors(session_id: str):
    """세션의 작성자 목록 조회"""
    try:
        if session_id not in user_sessions:
            return {
                "success": True,
                "authors": [],
                "message": "세션에 데이터가 없습니다."
            }
        
        session_chatbot = user_sessions[session_id]
        search_system = session_chatbot.search_system
        
        # 메타데이터에서 작성자 정보 추출
        authors = set()
        if hasattr(search_system.vector_db, 'metadata') and search_system.vector_db.metadata:
            for metadata in search_system.vector_db.metadata:
                author = metadata.get('author') or metadata.get('writer') or metadata.get('user_name')
                if author:
                    authors.add(author)
        
        return {
            "success": True,
            "authors": list(authors),
            "total_authors": len(authors)
        }
        
    except Exception as e:
        logger.error(f"❌ 작성자 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AuthorSelectionRequest(BaseModel):
    session_id: str
    author_name: str


@app.post("/api/select-author")
async def select_author(request: AuthorSelectionRequest):
    """특정 작성자 선택 및 해당 작성자의 데이터만으로 페르소나 설정"""
    try:
        session_chatbot = get_chatbot(request.session_id)
        search_system = session_chatbot.search_system
        
        if not hasattr(search_system.vector_db, 'metadata') or not search_system.vector_db.metadata:
            raise HTTPException(status_code=400, detail="세션에 업로드된 데이터가 없습니다.")
        
        # 선택된 작성자의 데이터만 필터링
        author_data = []
        author_texts = []
        author_embeddings = []
        author_metadata = []
        
        for i, metadata in enumerate(search_system.vector_db.metadata):
            author = metadata.get('author') or metadata.get('writer') or metadata.get('user_name')
            if author == request.author_name:
                author_data.append(metadata)
                author_texts.append(metadata.get('content', ''))
                if hasattr(search_system.vector_db, 'vectors') and i < len(search_system.vector_db.vectors):
                    author_embeddings.append(search_system.vector_db.vectors[i])
                author_metadata.append(metadata)
        
        if not author_data:
            raise HTTPException(status_code=404, detail=f"작성자 '{request.author_name}'의 데이터를 찾을 수 없습니다.")
        
        # 새로운 벡터 DB 생성 (해당 작성자만)
        if author_embeddings:
            import numpy as np
            author_embeddings_array = np.array(author_embeddings)
            
            # 새 인덱스 생성
            search_system.vector_db.create_index(author_embeddings_array.shape[1], index_type="Flat")
            search_system.vector_db.add_vectors(author_embeddings_array, author_metadata)
        
        # 세션에 선택된 작성자 정보 저장
        if not hasattr(session_chatbot, 'selected_author'):
            session_chatbot.selected_author = {}
        session_chatbot.selected_author = {
            'name': request.author_name,
            'data_count': len(author_data),
            'selected_at': datetime.now().isoformat()
        }
        
        logger.info(f"👤 작성자 선택: {request.author_name}, 데이터 {len(author_data)}개, 세션 {request.session_id}")
        
        return {
            "success": True,
            "message": f"작성자 '{request.author_name}'이 선택되었습니다.",
            "author_name": request.author_name,
            "data_count": len(author_data),
            "session_id": request.session_id
        }
        
    except Exception as e:
        logger.error(f"❌ 작성자 선택 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info("🚀 FastAPI 서버 시작...")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 