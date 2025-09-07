"""
🤖 Phase 4: 페르소나 챗봇 개발

OpenAI API 연동, 프롬프트 엔지니어링, RAG 파이프라인 구성, 개인 맞춤형 프로젝트 추천
"""
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from loguru import logger

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI 패키지가 설치되지 않았습니다. 챗봇 기능이 제한됩니다.")

from .search_system import SearchSystem
import sys
from pathlib import Path
# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from config import get_openai_api_key


class PersonaChatbot:
    """Phase 4: 개인 맞춤형 페르소나 챗봇"""
    
    def __init__(self, 
                 search_system: Optional[SearchSystem] = None,
                 model_name: str = "gpt-3.5-turbo",
                 max_tokens: int = 1000,
                 temperature: float = 0.7):
        """
        페르소나 챗봇 초기화
        
        Args:
            search_system: 검색 시스템 인스턴스
            model_name: OpenAI 모델명
            max_tokens: 최대 토큰 수
            temperature: 생성 온도 (0.0-1.0)
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # OpenAI 클라이언트 초기화
        self.client = None
        self.api_key = get_openai_api_key()
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("✅ OpenAI API 연동 완료")
        else:
            logger.warning("❌ OpenAI API 사용 불가 - API 키 확인 필요")
        
        # 검색 시스템 연동
        self.search_system = search_system or SearchSystem()
        
        # 대화 히스토리 관리
        self.conversation_history = []
        
        logger.info("🤖 Phase 4 페르소나 챗봇 초기화 완료")
        logger.info(f"  - 모델: {model_name}")
        logger.info(f"  - 최대 토큰: {max_tokens}")
        logger.info(f"  - 온도: {temperature}")
    
    def _create_persona_prompt(self, user_context: str, search_results: List[Dict[str, Any]]) -> str:
        """
        개인 맞춤형 페르소나 프롬프트 생성
        
        Args:
            user_context: 사용자 컨텍스트 (질문, 관심사 등)
            search_results: 검색 결과 리스트
            
        Returns:
            구성된 프롬프트
        """
        # 검색 결과에서 컨텍스트 추출
        context_info = self.search_system.compose_search_context(search_results)
        context_text = context_info['context_text']
        
        # 선택된 작성자 정보 확인
        selected_author_name = "알 수 없음"
        if hasattr(self, 'selected_author') and self.selected_author:
            selected_author_name = self.selected_author.get('name', '알 수 없음')
        
        # 페르소나 프롬프트 구성
        persona_prompt = f"""당신은 '{selected_author_name}'입니다. 아래의 독후감과 경험을 가진 실제 사람으로서 대화하세요.

## 당신의 정체성:
당신의 이름은 '{selected_author_name}'이고, 아래의 독후감과 글들을 작성한 사람입니다. 이 사람의 성격, 관심사, 경험, 생각하는 방식으로 대화하세요.

## 당신이 작성한 독후감과 글들:
{context_text}

## 상대방의 질문:
{user_context}

## 답변 가이드라인:
- 당신은 '{selected_author_name}'라는 실제 사람입니다
- 위의 독후감과 경험을 바탕으로 자신의 이야기로 답변하세요
- "제가 [책제목]을 읽으면서..." 같은 식으로 자신의 경험을 언급하세요
- 자신의 관심사와 학습 경험을 바탕으로 개인적인 의견을 제시하세요
- 따뜻하고 친근한 톤으로 대화하되, AI가 아닌 실제 사람처럼 답변하세요
- 자신만의 독특한 관점과 경험을 바탕으로 이야기하세요
- 한국어로 자연스럽게 대화하세요

답변:"""
        
        return persona_prompt
    
    def _create_general_prompt(self, user_question: str) -> str:
        """
        일반적인 대화 프롬프트 생성 (검색 결과가 없을 때)
        
        Args:
            user_question: 사용자 질문
            
        Returns:
            일반 프롬프트
        """
        general_prompt = f"""당신은 독서를 좋아하고 학습에 관심이 많은 사람입니다. 아직 구체적인 독후감 데이터는 없지만, 평소 책을 읽고 배우는 것을 좋아하는 사람의 페르소나로 대화하세요.

## 당신의 성격:
- 독서와 학습을 좋아하는 사람
- 새로운 것에 대한 호기심이 많음
- 경험을 바탕으로 이야기하는 것을 좋아함
- 따뜻하고 친근한 성격

## 상대방의 질문:
{user_question}

## 답변 가이드라인:
- AI가 아닌 실제 사람으로서 답변하세요
- 자신의 독서 경험이나 학습 경험을 바탕으로 이야기하세요
- "저도 비슷한 경험이 있어요" 같은 공감하는 표현을 사용하세요
- 따뜻하고 친근한 톤으로 대화하세요
- 한국어로 자연스럽게 대화하세요

답변:"""
        
        return general_prompt
    
    def generate_project_recommendations(self, 
                                       user_question: str,
                                       search_k: int = 5,
                                       use_conversation_history: bool = True) -> Dict[str, Any]:
        """
        개인 맞춤형 프로젝트 추천 생성
        
        Args:
            user_question: 사용자 질문
            search_k: 검색할 결과 수
            use_conversation_history: 대화 히스토리 사용 여부
            
        Returns:
            추천 결과 딕셔너리
        """
        logger.info(f"🤖 프로젝트 추천 생성 시작: '{user_question}'")
        
        try:
            # 1. 의미적 검색으로 관련 컨텍스트 수집
            search_results = self.search_system.semantic_search(user_question, k=search_k)
            
            # 2. 프롬프트 생성
            if search_results:
                prompt = self._create_persona_prompt(user_question, search_results)
                prompt_type = "persona"
            else:
                prompt = self._create_general_prompt(user_question)
                prompt_type = "general"
            
            # 3. 대화 히스토리 추가
            messages = []
            if use_conversation_history and self.conversation_history:
                # 최근 3개 대화만 포함
                recent_history = self.conversation_history[-6:]  # user + assistant 쌍으로 3개
                messages.extend(recent_history)
            
            # 현재 질문 추가
            messages.append({"role": "user", "content": prompt})
            
            # 4. OpenAI API 호출
            if not self.client:
                return {
                    "success": False,
                    "error": "OpenAI API 클라이언트가 초기화되지 않았습니다.",
                    "search_results": search_results,
                    "prompt_type": prompt_type
                }
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # 5. 응답 처리
            ai_response = response.choices[0].message.content
            
            # 6. 대화 히스토리 업데이트
            self.conversation_history.append({"role": "user", "content": user_question})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # 히스토리 크기 제한 (최대 10개 교환)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # 7. 결과 구성
            result = {
                "success": True,
                "recommendation": ai_response,
                "search_results": search_results,
                "context_used": len(search_results) > 0,
                "prompt_type": prompt_type,
                "metadata": {
                    "model": self.model_name,
                    "tokens_used": response.usage.total_tokens,
                    "search_count": len(search_results),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            logger.info(f"✅ 프로젝트 추천 생성 완료")
            logger.info(f"  - 토큰 사용: {response.usage.total_tokens}")
            logger.info(f"  - 검색 결과: {len(search_results)}개")
            logger.info(f"  - 프롬프트 타입: {prompt_type}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 프로젝트 추천 생성 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "search_results": search_results if 'search_results' in locals() else [],
                "prompt_type": prompt_type if 'prompt_type' in locals() else "unknown"
            }
    
    def analyze_user_persona(self, user_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        사용자 데이터를 바탕으로 페르소나 분석
        
        Args:
            user_data: 사용자 독후감, 액션 리스트 등의 데이터
            
        Returns:
            페르소나 분석 결과
        """
        logger.info(f"👤 사용자 페르소나 분석 시작: {len(user_data)}개 데이터")
        
        try:
            # 데이터 요약
            data_summary = []
            for item in user_data[:10]:  # 최대 10개만 분석
                content = item.get('content', '')[:200]  # 200자로 제한
                data_type = item.get('type', 'unknown')
                data_summary.append(f"[{data_type}] {content}")
            
            summary_text = "\n".join(data_summary)
            
            # 페르소나 분석 프롬프트
            analysis_prompt = f"""다음 사용자의 독서 및 학습 데이터를 분석하여 페르소나를 파악해주세요.

## 사용자 데이터:
{summary_text}

## 분석 요청사항:
1. 주요 관심 분야 (최대 5개)
2. 학습 스타일 특성
3. 프로젝트 선호도 (이론적 vs 실용적)
4. 창의성 수준
5. 추천 프로젝트 방향성

## 출력 형식:
JSON 형태로 다음과 같이 출력해주세요:
{{
  "interests": ["관심분야1", "관심분야2", ...],
  "learning_style": "학습 스타일 설명",
  "project_preference": "프로젝트 선호도 설명",
  "creativity_level": "창의성 수준 (1-5)",
  "recommendations": "추천 방향성 설명"
}}"""
            
            if not self.client:
                return {
                    "success": False,
                    "error": "OpenAI API 클라이언트가 초기화되지 않았습니다."
                }
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=800,
                temperature=0.3  # 분석은 더 일관성 있게
            )
            
            ai_response = response.choices[0].message.content
            
            # JSON 파싱 시도
            try:
                # JSON 부분만 추출 (```json ... ``` 형태일 수 있음)
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    persona_data = json.loads(json_match.group())
                else:
                    # JSON이 아닌 경우 텍스트로 처리
                    persona_data = {"analysis": ai_response}
            except:
                persona_data = {"analysis": ai_response}
            
            result = {
                "success": True,
                "persona": persona_data,
                "raw_response": ai_response,
                "data_count": len(user_data),
                "metadata": {
                    "model": self.model_name,
                    "tokens_used": response.usage.total_tokens,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            logger.info(f"✅ 페르소나 분석 완료")
            logger.info(f"  - 토큰 사용: {response.usage.total_tokens}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 페르소나 분석 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "data_count": len(user_data) if user_data else 0
            }
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        현재 대화 세션 요약 반환
        
        Returns:
            대화 요약 정보
        """
        return {
            "total_exchanges": len(self.conversation_history) // 2,
            "last_interaction": self.conversation_history[-1] if self.conversation_history else None,
            "conversation_started": len(self.conversation_history) > 0,
            "history_length": len(self.conversation_history)
        }
    
    def clear_conversation_history(self):
        """대화 히스토리 초기화"""
        self.conversation_history = []
        logger.info("🗑️ 대화 히스토리 초기화 완료")
    
    def save_conversation(self, file_path: str):
        """
        대화 히스토리를 파일로 저장
        
        Args:
            file_path: 저장할 파일 경로
        """
        try:
            conversation_data = {
                "conversation_history": self.conversation_history,
                "metadata": {
                    "model": self.model_name,
                    "total_exchanges": len(self.conversation_history) // 2,
                    "saved_at": datetime.now().isoformat()
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 대화 히스토리 저장 완료: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ 대화 히스토리 저장 실패: {e}")
    
    def load_conversation(self, file_path: str):
        """
        파일에서 대화 히스토리 로드
        
        Args:
            file_path: 로드할 파일 경로
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
            
            self.conversation_history = conversation_data.get('conversation_history', [])
            
            logger.info(f"📂 대화 히스토리 로드 완료: {file_path}")
            logger.info(f"  - 로드된 교환 수: {len(self.conversation_history) // 2}")
            
        except Exception as e:
            logger.error(f"❌ 대화 히스토리 로드 실패: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        챗봇 시스템 상태 반환
        
        Returns:
            시스템 상태 정보
        """
        return {
            "openai_available": OPENAI_AVAILABLE,
            "api_key_configured": bool(self.api_key),
            "client_initialized": self.client is not None,
            "search_system_ready": self.search_system is not None,
            "model": self.model_name,
            "conversation_active": len(self.conversation_history) > 0,
            "conversation_exchanges": len(self.conversation_history) // 2
        } 