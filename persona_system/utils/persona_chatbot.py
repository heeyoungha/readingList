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
        
        # 페르소나 프롬프트 구성
        persona_prompt = f"""당신은 사용자의 독서 패턴과 관심사를 분석하여 개인 맞춤형 프로젝트를 추천하는 AI 어시스턴트입니다.

## 당신의 역할:
1. 사용자의 독후감, 액션 리스트, 관심사를 바탕으로 페르소나를 파악
2. 창의적이고 실현 가능한 프로젝트 아이디어 제안
3. 사용자의 성향과 능력에 맞는 구체적인 실행 방안 제시
4. 따뜻하고 격려적인 톤으로 대화

## 사용자 관련 정보:
{context_text}

## 사용자 질문:
{user_context}

## 답변 가이드라인:
- 위의 사용자 정보를 바탕으로 개인화된 추천 제공
- 구체적이고 실행 가능한 프로젝트 아이디어 제시
- 단계별 실행 계획 포함
- 사용자의 관심사와 연결된 창의적 접근
- 한국어로 친근하고 격려적인 톤 사용

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
        general_prompt = f"""당신은 창의적인 프로젝트 아이디어를 제안하는 친근한 AI 어시스턴트입니다.

## 당신의 역할:
1. 사용자의 관심사에 맞는 창의적 프로젝트 아이디어 제안
2. 실현 가능하고 구체적인 실행 방안 제시
3. 단계별 가이드 및 필요한 리소스 안내
4. 격려적이고 동기부여가 되는 대화

## 사용자 질문:
{user_question}

## 답변 가이드라인:
- 창의적이고 실현 가능한 아이디어 제시
- 구체적인 실행 단계 포함
- 필요한 도구나 리소스 안내
- 한국어로 친근하고 격려적인 톤 사용

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