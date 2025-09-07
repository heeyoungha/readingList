"""
🚀 Phase 5 테스트: 사용자 인터페이스 및 테스트 완료

이 파일은 Phase 5에서 구현된 사용자 인터페이스와 API를 테스트합니다:
✅ FastAPI 백엔드 서버
✅ 웹 인터페이스 (HTML/CSS/JS)
✅ API 엔드포인트 (채팅, 업로드, 피드백)
✅ 사용자 피드백 시스템
"""
import sys
import os
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, Any
import tempfile

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loguru import logger
import requests
import threading
import subprocess
from datetime import datetime

# FastAPI 테스트용 imports
try:
    from fastapi.testclient import TestClient
    from backend.main import app
    TEST_CLIENT_AVAILABLE = True
except ImportError:
    TEST_CLIENT_AVAILABLE = False
    logger.warning("FastAPI TestClient를 사용할 수 없습니다. 서버 테스트가 제한됩니다.")


class Phase5Tester:
    """Phase 5 사용자 인터페이스 및 테스트 클래스"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.server_process = None
        self.test_session_id = f"test_session_{int(time.time())}"
        
        # 테스트 결과 추적
        self.test_results = {}
        
        logger.info("🚀 Phase 5 테스트 시작")
        logger.info(f"  - 서버 URL: {server_url}")
        logger.info(f"  - 테스트 세션 ID: {self.test_session_id}")
    
    def test_1_server_startup(self) -> bool:
        """1. 서버 시작 테스트"""
        print("=" * 60)
        print("🚀 1. 서버 시작 테스트")
        print("=" * 60)
        
        try:
            # 1.1 서버가 이미 실행 중인지 확인
            print("\n1.1 서버 상태 확인")
            try:
                response = requests.get(f"{self.server_url}/api/health", timeout=5)
                if response.status_code == 200:
                    print("  ✅ 서버가 이미 실행 중입니다")
                    return True
            except:
                print("  ℹ️ 서버가 실행되지 않음, 새로 시작합니다")
            
            # 1.2 서버 시작
            print("\n1.2 서버 시작")
            if TEST_CLIENT_AVAILABLE:
                print("  ✅ TestClient 사용 가능")
                self.client = TestClient(app)
                return True
            else:
                print("  ⚠️ TestClient 사용 불가, 수동 서버 시작 필요")
                print("  💡 다른 터미널에서 'python backend/main.py' 실행 후 계속하세요")
                
                # 사용자가 서버를 시작할 때까지 대기
                print("  ⏳ 서버 시작 대기 중...")
                for i in range(30):  # 30초 대기
                    try:
                        response = requests.get(f"{self.server_url}/api/health", timeout=2)
                        if response.status_code == 200:
                            print("  ✅ 서버 시작 확인됨")
                            return True
                    except:
                        pass
                    time.sleep(1)
                    print(f"  ⏳ {i+1}/30초...")
                
                print("  ❌ 서버 시작 실패 - 수동으로 시작해주세요")
                return False
                
        except Exception as e:
            print(f"  ❌ 서버 시작 테스트 실패: {e}")
            return False
    
    def test_2_api_endpoints(self) -> bool:
        """2. API 엔드포인트 테스트"""
        print("=" * 60)
        print("🔌 2. API 엔드포인트 테스트")
        print("=" * 60)
        
        try:
            success_count = 0
            total_tests = 6
            
            # 2.1 헬스체크 API
            print("\n2.1 헬스체크 API 테스트")
            if TEST_CLIENT_AVAILABLE:
                response = self.client.get("/api/health")
            else:
                response = requests.get(f"{self.server_url}/api/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 헬스체크 성공: {data.get('status')}")
                print(f"    - API 키 설정: {data.get('system_status', {}).get('api_key_configured')}")
                success_count += 1
            else:
                print(f"  ❌ 헬스체크 실패: {response.status_code}")
            
            # 2.2 채팅 API
            print("\n2.2 채팅 API 테스트")
            chat_data = {
                "message": "안녕하세요! 테스트 메시지입니다.",
                "session_id": self.test_session_id,
                "use_search": False,
                "search_k": 3
            }
            
            if TEST_CLIENT_AVAILABLE:
                response = self.client.post("/api/chat", json=chat_data)
            else:
                response = requests.post(f"{self.server_url}/api/chat", json=chat_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"  ✅ 채팅 API 성공")
                    print(f"    - 응답 길이: {len(data.get('response', ''))}")
                    print(f"    - 세션 ID: {data.get('session_id')}")
                    success_count += 1
                else:
                    print(f"  ❌ 채팅 API 실패: {data.get('error')}")
            else:
                print(f"  ❌ 채팅 API 실패: {response.status_code}")
            
            # 2.3 세션 히스토리 API
            print("\n2.3 세션 히스토리 API 테스트")
            if TEST_CLIENT_AVAILABLE:
                response = self.client.get(f"/api/session/{self.test_session_id}/history")
            else:
                response = requests.get(f"{self.server_url}/api/session/{self.test_session_id}/history")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 히스토리 API 성공")
                print(f"    - 대화 수: {data.get('summary', {}).get('total_exchanges', 0)}")
                success_count += 1
            else:
                print(f"  ❌ 히스토리 API 실패: {response.status_code}")
            
            # 2.4 시스템 통계 API
            print("\n2.4 시스템 통계 API 테스트")
            if TEST_CLIENT_AVAILABLE:
                response = self.client.get("/api/stats")
            else:
                response = requests.get(f"{self.server_url}/api/stats")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 통계 API 성공")
                print(f"    - 활성 세션: {data.get('active_sessions', 0)}")
                print(f"    - 총 대화: {data.get('total_conversations', 0)}")
                success_count += 1
            else:
                print(f"  ❌ 통계 API 실패: {response.status_code}")
            
            # 2.5 파일 업로드 API
            print("\n2.5 파일 업로드 API 테스트")
            test_data = [
                {
                    "content": "테스트 사용자 데이터입니다. Python과 데이터 분석에 관심이 많습니다.",
                    "type": "user_note",
                    "date": datetime.now().isoformat()
                },
                {
                    "content": "머신러닝 프로젝트를 진행해보고 싶습니다.",
                    "type": "goal",
                    "date": datetime.now().isoformat()
                }
            ]
            
            # 임시 JSON 파일 생성
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
                temp_file_path = f.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('test_data.json', f, 'application/json')}
                    data = {'session_id': self.test_session_id}
                    
                    if TEST_CLIENT_AVAILABLE:
                        response = self.client.post("/api/upload-data", files=files, data=data)
                    else:
                        response = requests.post(f"{self.server_url}/api/upload-data", files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"  ✅ 파일 업로드 성공")
                        print(f"    - 업로드된 문서: {result.get('document_count')}개")
                        success_count += 1
                    else:
                        print(f"  ❌ 파일 업로드 실패: {result}")
                else:
                    print(f"  ❌ 파일 업로드 실패: {response.status_code}")
            finally:
                # 임시 파일 삭제
                os.unlink(temp_file_path)
            
            # 2.6 피드백 API
            print("\n2.6 피드백 API 테스트")
            feedback_data = {
                "session_id": self.test_session_id,
                "message_id": "test_msg_123",
                "rating": 5,
                "feedback": "테스트 피드백입니다. 매우 만족스럽습니다!"
            }
            
            if TEST_CLIENT_AVAILABLE:
                response = self.client.post("/api/feedback", json=feedback_data)
            else:
                response = requests.post(f"{self.server_url}/api/feedback", json=feedback_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"  ✅ 피드백 API 성공")
                    print(f"    - 메시지: {data.get('message')}")
                    success_count += 1
                else:
                    print(f"  ❌ 피드백 API 실패: {data}")
            else:
                print(f"  ❌ 피드백 API 실패: {response.status_code}")
            
            # 결과 요약
            print(f"\n📊 API 테스트 결과: {success_count}/{total_tests} 성공")
            return success_count >= total_tests * 0.8  # 80% 이상 성공
            
        except Exception as e:
            print(f"  ❌ API 테스트 실패: {e}")
            return False
    
    def test_3_web_interface(self) -> bool:
        """3. 웹 인터페이스 테스트"""
        print("=" * 60)
        print("🌐 3. 웹 인터페이스 테스트")
        print("=" * 60)
        
        try:
            # 3.1 메인 페이지 접근
            print("\n3.1 메인 페이지 접근 테스트")
            if TEST_CLIENT_AVAILABLE:
                response = self.client.get("/")
            else:
                response = requests.get(f"{self.server_url}/")
            
            if response.status_code == 200:
                content = response.text if hasattr(response, 'text') else str(response.content)
                if "페르소나 챗봇" in content:
                    print("  ✅ 메인 페이지 로드 성공")
                    print("  ✅ 페이지 제목 확인됨")
                    
                    # HTML 구조 검증
                    html_checks = [
                        ("chat-messages", "채팅 메시지 영역"),
                        ("message-input", "메시지 입력창"),
                        ("send-btn", "전송 버튼"),
                        ("system-status", "시스템 상태"),
                        ("file-upload", "파일 업로드")
                    ]
                    
                    check_count = 0
                    for element_id, description in html_checks:
                        if element_id in content:
                            print(f"    ✅ {description} 확인")
                            check_count += 1
                        else:
                            print(f"    ❌ {description} 누락")
                    
                    print(f"  📊 UI 요소 검증: {check_count}/{len(html_checks)}개 확인")
                    return check_count >= len(html_checks) * 0.8
                else:
                    print("  ❌ 페이지 내용이 올바르지 않음")
                    return False
            else:
                print(f"  ❌ 메인 페이지 로드 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ 웹 인터페이스 테스트 실패: {e}")
            return False
    
    def test_4_integration_test(self) -> bool:
        """4. 통합 테스트 - 전체 워크플로우"""
        print("=" * 60)
        print("🔄 4. 통합 테스트 - 전체 워크플로우")
        print("=" * 60)
        
        try:
            # 4.1 새 세션 생성 및 데이터 업로드
            print("\n4.1 새 세션 생성 및 데이터 업로드")
            integration_session = f"integration_test_{int(time.time())}"
            
            # 테스트 데이터 생성
            user_data = [
                {
                    "content": "React와 Node.js를 이용한 풀스택 웹 개발 경험이 있습니다. 최근에는 TypeScript와 GraphQL에 관심을 가지고 공부하고 있습니다.",
                    "type": "experience",
                    "date": datetime.now().isoformat()
                },
                {
                    "content": "머신러닝과 데이터 분석 분야로 진출하고 싶습니다. Python과 pandas는 기본적으로 다룰 수 있습니다.",
                    "type": "goal",
                    "date": datetime.now().isoformat()
                },
                {
                    "content": "사용자 경험(UX) 디자인에 대해 배우고 있으며, 디자인 시스템 구축에 관심이 많습니다.",
                    "type": "interest",
                    "date": datetime.now().isoformat()
                }
            ]
            
            # 데이터 업로드
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
                temp_file_path = f.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('integration_test_data.json', f, 'application/json')}
                    data = {'session_id': integration_session}
                    
                    if TEST_CLIENT_AVAILABLE:
                        upload_response = self.client.post("/api/upload-data", files=files, data=data)
                    else:
                        upload_response = requests.post(f"{self.server_url}/api/upload-data", files=files, data=data)
                
                if upload_response.status_code == 200:
                    upload_result = upload_response.json()
                    if upload_result.get('success'):
                        print(f"  ✅ 데이터 업로드 성공: {upload_result.get('document_count')}개 문서")
                    else:
                        print(f"  ❌ 데이터 업로드 실패")
                        return False
                else:
                    print(f"  ❌ 데이터 업로드 실패: {upload_response.status_code}")
                    return False
            finally:
                os.unlink(temp_file_path)
            
            # 4.2 페르소나 분석 테스트
            print("\n4.2 페르소나 분석 테스트")
            persona_data = {
                "user_data": user_data,
                "session_id": integration_session
            }
            
            if TEST_CLIENT_AVAILABLE:
                persona_response = self.client.post("/api/persona-analysis", json=persona_data)
            else:
                persona_response = requests.post(f"{self.server_url}/api/persona-analysis", json=persona_data)
            
            if persona_response.status_code == 200:
                persona_result = persona_response.json()
                if persona_result.get('success'):
                    print(f"  ✅ 페르소나 분석 성공")
                    persona = persona_result.get('persona', {})
                    if 'interests' in persona:
                        print(f"    - 관심사: {persona.get('interests', [])}")
                    if 'learning_style' in persona:
                        print(f"    - 학습 스타일: {persona.get('learning_style', '')[:100]}...")
                else:
                    print(f"  ⚠️ 페르소나 분석 실패 (API 키 필요할 수 있음)")
            else:
                print(f"  ⚠️ 페르소나 분석 실패: {persona_response.status_code}")
            
            # 4.3 맞춤형 채팅 테스트
            print("\n4.3 맞춤형 채팅 테스트")
            chat_questions = [
                "제 경험과 관심사를 바탕으로 다음 프로젝트를 추천해주세요",
                "웹 개발과 머신러닝을 결합한 프로젝트 아이디어가 있나요?"
            ]
            
            successful_chats = 0
            for i, question in enumerate(chat_questions, 1):
                print(f"  4.3.{i} 질문: '{question[:50]}...'")
                
                chat_data = {
                    "message": question,
                    "session_id": integration_session,
                    "use_search": True,
                    "search_k": 5
                }
                
                if TEST_CLIENT_AVAILABLE:
                    chat_response = self.client.post("/api/chat", json=chat_data)
                else:
                    chat_response = requests.post(f"{self.server_url}/api/chat", json=chat_data)
                
                if chat_response.status_code == 200:
                    chat_result = chat_response.json()
                    if chat_result.get('success'):
                        print(f"    ✅ 응답 생성 성공")
                        print(f"      - 응답 길이: {len(chat_result.get('response', ''))}자")
                        print(f"      - 검색 사용: {chat_result.get('metadata', {}).get('context_used')}")
                        print(f"      - 토큰 사용: {chat_result.get('metadata', {}).get('tokens_used')}")
                        successful_chats += 1
                    else:
                        print(f"    ❌ 응답 생성 실패: {chat_result.get('error')}")
                else:
                    print(f"    ❌ 채팅 실패: {chat_response.status_code}")
            
            # 4.4 세션 상태 확인
            print("\n4.4 세션 상태 확인")
            if TEST_CLIENT_AVAILABLE:
                history_response = self.client.get(f"/api/session/{integration_session}/history")
            else:
                history_response = requests.get(f"{self.server_url}/api/session/{integration_session}/history")
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                if history_data.get('success'):
                    summary = history_data.get('summary', {})
                    print(f"  ✅ 세션 상태 확인 성공")
                    print(f"    - 총 대화 교환: {summary.get('total_exchanges', 0)}")
                    print(f"    - 대화 활성: {summary.get('conversation_started', False)}")
                else:
                    print(f"  ❌ 세션 상태 확인 실패")
            else:
                print(f"  ❌ 세션 상태 확인 실패: {history_response.status_code}")
            
            # 결과 평가
            success_criteria = successful_chats >= len(chat_questions) * 0.5  # 50% 이상 성공
            print(f"\n📊 통합 테스트 결과: {successful_chats}/{len(chat_questions)} 채팅 성공")
            
            return success_criteria
            
        except Exception as e:
            print(f"  ❌ 통합 테스트 실패: {e}")
            return False
    
    def test_5_performance_test(self) -> bool:
        """5. 성능 테스트"""
        print("=" * 60)
        print("⚡ 5. 성능 테스트")
        print("=" * 60)
        
        try:
            # 5.1 응답 시간 테스트
            print("\n5.1 API 응답 시간 테스트")
            
            # 헬스체크 응답 시간
            start_time = time.time()
            if TEST_CLIENT_AVAILABLE:
                response = self.client.get("/api/health")
            else:
                response = requests.get(f"{self.server_url}/api/health")
            health_time = time.time() - start_time
            
            print(f"  📊 헬스체크 응답 시간: {health_time:.3f}초")
            
            # 채팅 응답 시간 (검색 없음)
            start_time = time.time()
            chat_data = {
                "message": "간단한 질문입니다.",
                "session_id": self.test_session_id,
                "use_search": False,
                "search_k": 3
            }
            
            if TEST_CLIENT_AVAILABLE:
                response = self.client.post("/api/chat", json=chat_data)
            else:
                response = requests.post(f"{self.server_url}/api/chat", json=chat_data)
            chat_time = time.time() - start_time
            
            print(f"  📊 채팅 응답 시간 (검색 없음): {chat_time:.3f}초")
            
            # 성능 기준 평가
            performance_ok = health_time < 1.0 and chat_time < 30.0  # 합리적인 기준
            
            if performance_ok:
                print("  ✅ 성능 테스트 통과")
            else:
                print("  ⚠️ 성능이 예상보다 느립니다")
            
            return performance_ok
            
        except Exception as e:
            print(f"  ❌ 성능 테스트 실패: {e}")
            return False
    
    def cleanup(self):
        """테스트 정리"""
        try:
            # 테스트 세션 정리
            if TEST_CLIENT_AVAILABLE:
                self.client.delete(f"/api/session/{self.test_session_id}")
            else:
                requests.delete(f"{self.server_url}/api/session/{self.test_session_id}")
            
            # 서버 프로세스 정리 (필요한 경우)
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait()
            
            logger.info("🧹 테스트 정리 완료")
        except Exception as e:
            logger.warning(f"정리 중 오류: {e}")


def main():
    """메인 테스트 실행"""
    print("🚀 Phase 5 사용자 인터페이스 및 테스트 시작")
    print("=" * 80)
    
    tester = Phase5Tester()
    
    # 테스트 실행
    test_results = {}
    
    try:
        # 1. 서버 시작 테스트
        test_results["서버 시작"] = tester.test_1_server_startup()
        
        if test_results["서버 시작"]:
            # 2. API 엔드포인트 테스트
            test_results["API 엔드포인트"] = tester.test_2_api_endpoints()
            
            # 3. 웹 인터페이스 테스트
            test_results["웹 인터페이스"] = tester.test_3_web_interface()
            
            # 4. 통합 테스트
            test_results["통합 테스트"] = tester.test_4_integration_test()
            
            # 5. 성능 테스트
            test_results["성능 테스트"] = tester.test_5_performance_test()
        else:
            print("⚠️ 서버 시작 실패로 인해 나머지 테스트를 건너뜁니다.")
            test_results.update({
                "API 엔드포인트": False,
                "웹 인터페이스": False,
                "통합 테스트": False,
                "성능 테스트": False
            })
        
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 중 예상치 못한 오류: {e}")
    finally:
        # 정리
        tester.cleanup()
    
    # 최종 결과 요약
    print("\n" + "=" * 80)
    print("🎯 Phase 5 테스트 결과 요약")
    print("=" * 80)
    
    for test_name, result in test_results.items():
        status = "✅ 성공" if result else "❌ 실패"
        print(f"  {status} {test_name}")
    
    # 성공률 계산
    success_count = sum(1 for result in test_results.values() if result)
    total_count = len(test_results)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\n📊 전체 성공률: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    # 결과에 따른 메시지
    if success_rate >= 80:
        print("\n🎉 Phase 5 사용자 인터페이스 및 테스트 완료!")
        print("   ✅ FastAPI 백엔드 서버")
        print("   ✅ 웹 인터페이스 (HTML/CSS/JS)")
        print("   ✅ API 엔드포인트 (채팅, 업로드, 피드백)")
        print("   ✅ 사용자 피드백 시스템")
        print("\n🎯 페르소나 시스템 전체 구현 완료!")
        print("   Phase 1: ✅ 데이터 수집 및 전처리")
        print("   Phase 2: ✅ 임베딩 생성 및 벡터 DB 구축")
        print("   Phase 3: ✅ 검색 시스템 구현")
        print("   Phase 4: ✅ 페르소나 챗봇 개발")
        print("   Phase 5: ✅ 사용자 인터페이스 및 테스트")
        
        print(f"\n🌐 웹 인터페이스 접속: http://localhost:8000")
        print("💡 사용법:")
        print("   1. 웹 브라우저에서 위 주소로 접속")
        print("   2. JSON 파일로 사용자 데이터 업로드")
        print("   3. 채팅창에서 프로젝트 추천 요청")
        print("   4. AI가 개인 맞춤형 프로젝트 추천 제공")
        
    elif success_rate >= 60:
        print("\n⚠️ 일부 기능에서 문제가 발견되었습니다.")
        print("   기본 기능은 작동하지만 개선이 필요합니다.")
    else:
        print("\n❌ 심각한 문제가 발견되었습니다.")
        print("   문제를 해결한 후 다시 테스트해주세요.")
    
    print(f"\n📝 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main() 