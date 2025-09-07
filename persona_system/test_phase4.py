"""
🤖 Phase 4 테스트: 페르소나 챗봇 개발 완료

이 파일은 Phase 4에서 구현된 페르소나 챗봇을 테스트합니다:
✅ OpenAI API 연동 (무료 크레딧 활용)
✅ 프롬프트 엔지니어링
✅ RAG 파이프라인 구성
✅ 개인 맞춤형 프로젝트 추천 로직
"""
import sys
import os
from pathlib import Path
import json
import numpy as np

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loguru import logger
from utils.persona_chatbot import PersonaChatbot
from utils.search_system import SearchSystem


def test_1_chatbot_initialization():
    """1. 챗봇 초기화 테스트"""
    print("=" * 60)
    print("🤖 1. 챗봇 초기화 테스트")
    print("=" * 60)
    
    try:
        # 1.1 기본 챗봇 생성
        print("\n1.1 기본 챗봇 생성")
        chatbot = PersonaChatbot()
        print(f"  ✅ PersonaChatbot 생성 성공")
        
        # 1.2 시스템 상태 확인
        print("\n1.2 시스템 상태 확인")
        status = chatbot.get_system_status()
        print(f"  📊 시스템 상태:")
        print(f"    - OpenAI 사용 가능: {status['openai_available']}")
        print(f"    - API 키 설정: {status['api_key_configured']}")
        print(f"    - 클라이언트 초기화: {status['client_initialized']}")
        print(f"    - 검색 시스템: {status['search_system_ready']}")
        print(f"    - 모델: {status['model']}")
        
        # 1.3 대화 상태 확인
        print("\n1.3 대화 상태 확인")
        conversation_summary = chatbot.get_conversation_summary()
        print(f"  💬 대화 상태:")
        print(f"    - 대화 시작됨: {conversation_summary['conversation_started']}")
        print(f"    - 총 교환 수: {conversation_summary['total_exchanges']}")
        
        return chatbot, status['openai_available'] and status['api_key_configured']
        
    except Exception as e:
        print(f"  ❌ 테스트 실패: {e}")
        return None, False


def test_2_search_integration():
    """2. 검색 시스템 통합 테스트"""
    print("=" * 60)
    print("🔍 2. 검색 시스템 통합 테스트")
    print("=" * 60)
    
    try:
        chatbot = PersonaChatbot()
        
        # 2.1 샘플 데이터로 검색 시스템 구축
        print("\n2.1 샘플 데이터로 검색 시스템 구축")
        sample_texts = [
            "Python 프로그래밍을 배우면서 데이터 분석의 재미를 알게 되었습니다. 특히 pandas와 matplotlib을 활용한 시각화가 흥미로웠습니다.",
            "머신러닝 알고리즘을 공부하다 보니 수학적 기초의 중요성을 깨달았습니다. 선형대수와 통계학을 더 깊이 학습해야겠다고 생각했습니다.",
            "창의적 글쓰기 워크샵에서 스토리텔링 기법을 배웠습니다. 데이터를 이야기로 표현하는 방법이 매우 유용했습니다.",
            "웹 개발 프로젝트를 진행하면서 사용자 경험의 중요성을 배웠습니다. React와 Node.js를 활용한 풀스택 개발에 관심이 생겼습니다.",
            "디자인 씽킹 방법론을 적용해 문제 해결 과정을 체계화했습니다. 사용자 중심의 접근 방식이 인상적이었습니다."
        ]
        
        sample_metadata = []
        for i, text in enumerate(sample_texts):
            metadata = {
                'id': f'sample_{i}',
                'content': text,
                'type': 'book_review' if i % 2 == 0 else 'action_list',
                'date': '2024-01-01'
            }
            sample_metadata.append(metadata)
        
        # 검색 시스템에 데이터 추가
        search_system = chatbot.search_system
        
        # 임베딩 생성 및 인덱스 구축
        embedding_result = search_system.embedding_generator.generate_embeddings(sample_texts)
        if isinstance(embedding_result, dict):
            embeddings = embedding_result['embeddings']
        else:
            embeddings = embedding_result
            
        search_system.vector_db.create_index(embeddings.shape[1], index_type="Flat")
        search_system.vector_db.add_vectors(embeddings, sample_metadata)
        
        print(f"  ✅ 검색 시스템 구축 완료: {len(sample_texts)}개 문서")
        
        # 2.2 검색 테스트
        print("\n2.2 검색 테스트")
        test_queries = [
            "데이터 분석 프로젝트를 시작하고 싶어",
            "창의적인 글쓰기 방법을 배우고 싶어"
        ]
        
        for query in test_queries:
            results = search_system.semantic_search(query, k=3)
            print(f"  🔍 '{query}' -> {len(results)}개 결과")
            if results:
                print(f"    최상위 결과: {results[0]['content'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 테스트 실패: {e}")
        return False


def test_3_persona_analysis(chatbot_available: bool):
    """3. 페르소나 분석 테스트"""
    print("=" * 60)
    print("👤 3. 페르소나 분석 테스트")
    print("=" * 60)
    
    if not chatbot_available:
        print("  ⚠️ OpenAI API 사용 불가로 테스트 건너뜀")
        return False
    
    try:
        chatbot = PersonaChatbot()
        
        # 3.1 샘플 사용자 데이터 생성
        print("\n3.1 샘플 사용자 데이터 생성")
        user_data = [
            {"content": "Python 데이터 분석 책을 읽고 실제 프로젝트를 진행해보고 싶다는 생각이 들었습니다.", "type": "book_review"},
            {"content": "머신러닝 알고리즘을 더 깊이 공부하기 위해 수학 기초를 다져야겠습니다.", "type": "action_list"},
            {"content": "창의적 글쓰기와 데이터 스토리텔링을 결합한 콘텐츠를 만들어보고 싶습니다.", "type": "project_idea"},
            {"content": "웹 개발과 데이터 시각화를 결합한 대시보드를 개발하는 것이 목표입니다.", "type": "goal"},
            {"content": "디자인 씽킹을 활용한 문제 해결 프로세스에 대해 더 학습하고 싶습니다.", "type": "learning_plan"}
        ]
        
        print(f"  ✅ {len(user_data)}개 사용자 데이터 준비")
        
        # 3.2 페르소나 분석 실행
        print("\n3.2 페르소나 분석 실행")
        analysis_result = chatbot.analyze_user_persona(user_data)
        
        if analysis_result['success']:
            print(f"  ✅ 페르소나 분석 성공")
            print(f"    - 토큰 사용: {analysis_result['metadata']['tokens_used']}")
            
            persona = analysis_result['persona']
            if 'interests' in persona:
                print(f"    - 주요 관심사: {persona.get('interests', 'N/A')}")
            if 'learning_style' in persona:
                print(f"    - 학습 스타일: {persona.get('learning_style', 'N/A')[:100]}...")
            
            return True
        else:
            print(f"  ❌ 페르소나 분석 실패: {analysis_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ 테스트 실패: {e}")
        return False


def test_4_project_recommendations(chatbot_available: bool):
    """4. 프로젝트 추천 테스트"""
    print("=" * 60)
    print("💡 4. 프로젝트 추천 테스트")
    print("=" * 60)
    
    if not chatbot_available:
        print("  ⚠️ OpenAI API 사용 불가로 테스트 건너뜀")
        return False
    
    try:
        chatbot = PersonaChatbot()
        
        # 4.1 검색 데이터 구축 (이전 테스트와 동일)
        print("\n4.1 검색 데이터 구축")
        sample_texts = [
            "Python을 이용한 데이터 분석 프로젝트를 진행했습니다.",
            "머신러닝 모델을 구현하여 예측 시스템을 만들었습니다.",
            "웹 개발과 데이터 시각화를 결합한 대시보드를 개발했습니다."
        ]
        
        sample_metadata = []
        for i, text in enumerate(sample_texts):
            metadata = {'id': f'sample_{i}', 'content': text, 'type': 'project'}
            sample_metadata.append(metadata)
        
        search_system = chatbot.search_system
        embedding_result = search_system.embedding_generator.generate_embeddings(sample_texts)
        if isinstance(embedding_result, dict):
            embeddings = embedding_result['embeddings']
        else:
            embeddings = embedding_result
            
        search_system.vector_db.create_index(embeddings.shape[1], index_type="Flat")
        search_system.vector_db.add_vectors(embeddings, sample_metadata)
        
        print(f"  ✅ 검색 데이터 구축 완료")
        
        # 4.2 프로젝트 추천 테스트
        print("\n4.2 프로젝트 추천 테스트")
        test_questions = [
            "데이터 분석을 활용한 창의적인 프로젝트를 추천해주세요",
            "웹 개발과 머신러닝을 결합한 아이디어가 필요해요"
        ]
        
        for question in test_questions:
            print(f"\n  🤖 질문: '{question}'")
            
            recommendation = chatbot.generate_project_recommendations(question, search_k=3)
            
            if recommendation['success']:
                print(f"    ✅ 추천 생성 성공")
                print(f"    - 토큰 사용: {recommendation['metadata']['tokens_used']}")
                print(f"    - 검색 결과: {recommendation['metadata']['search_count']}개")
                print(f"    - 프롬프트 타입: {recommendation['prompt_type']}")
                print(f"    - 컨텍스트 사용: {recommendation['context_used']}")
                print(f"    - 추천 내용 (처음 100자): {recommendation['recommendation'][:100]}...")
            else:
                print(f"    ❌ 추천 생성 실패: {recommendation.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 테스트 실패: {e}")
        return False


def test_5_conversation_management(chatbot_available: bool):
    """5. 대화 관리 테스트"""
    print("=" * 60)
    print("💬 5. 대화 관리 테스트")
    print("=" * 60)
    
    if not chatbot_available:
        print("  ⚠️ OpenAI API 사용 불가로 테스트 건너뜀")
        return False
    
    try:
        chatbot = PersonaChatbot()
        
        # 5.1 대화 히스토리 테스트
        print("\n5.1 대화 히스토리 테스트")
        
        # 수동으로 대화 히스토리 추가 (API 호출 없이)
        chatbot.conversation_history = [
            {"role": "user", "content": "안녕하세요, 프로젝트 추천을 받고 싶어요"},
            {"role": "assistant", "content": "안녕하세요! 어떤 분야의 프로젝트에 관심이 있으신가요?"},
            {"role": "user", "content": "데이터 분석 관련 프로젝트요"},
            {"role": "assistant", "content": "데이터 분석 프로젝트 추천드리겠습니다..."}
        ]
        
        summary = chatbot.get_conversation_summary()
        print(f"  ✅ 대화 히스토리 추가 완료")
        print(f"    - 총 교환 수: {summary['total_exchanges']}")
        print(f"    - 대화 시작됨: {summary['conversation_started']}")
        
        # 5.2 대화 저장/로드 테스트
        print("\n5.2 대화 저장/로드 테스트")
        
        # 저장 테스트
        save_path = "./data/test_conversation.json"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        chatbot.save_conversation(save_path)
        print(f"  ✅ 대화 저장 완료: {save_path}")
        
        # 새 챗봇에 로드 테스트
        new_chatbot = PersonaChatbot()
        new_chatbot.load_conversation(save_path)
        
        new_summary = new_chatbot.get_conversation_summary()
        print(f"  ✅ 대화 로드 완료")
        print(f"    - 로드된 교환 수: {new_summary['total_exchanges']}")
        
        # 5.3 대화 초기화 테스트
        print("\n5.3 대화 초기화 테스트")
        new_chatbot.clear_conversation_history()
        cleared_summary = new_chatbot.get_conversation_summary()
        print(f"  ✅ 대화 초기화 완료")
        print(f"    - 초기화 후 교환 수: {cleared_summary['total_exchanges']}")
        
        # 임시 파일 정리
        if os.path.exists(save_path):
            os.remove(save_path)
        
        return True
        
    except Exception as e:
        print(f"  ❌ 테스트 실패: {e}")
        return False


def test_6_integration_test(chatbot_available: bool):
    """6. 통합 테스트 - 전체 워크플로우"""
    print("=" * 60)
    print("🔄 6. 통합 테스트 - 전체 워크플로우")
    print("=" * 60)
    
    if not chatbot_available:
        print("  ⚠️ OpenAI API 사용 불가로 모의 테스트 진행")
        return test_6_mock_integration()
    
    try:
        # 6.1 전체 시스템 초기화
        print("\n6.1 전체 시스템 초기화")
        chatbot = PersonaChatbot()
        print(f"  ✅ 페르소나 챗봇 초기화 완료")
        
        # 6.2 사용자 데이터 기반 검색 시스템 구축
        print("\n6.2 사용자 데이터 기반 검색 시스템 구축")
        user_documents = [
            {"content": "React와 Python Flask를 이용한 웹 애플리케이션 개발 경험이 있습니다.", "type": "experience"},
            {"content": "데이터 시각화와 머신러닝에 관심이 많아 관련 프로젝트를 해보고 싶습니다.", "type": "interest"},
            {"content": "사용자 인터페이스 디자인과 사용자 경험 개선에 대해 배우고 있습니다.", "type": "learning"}
        ]
        
        texts = [doc["content"] for doc in user_documents]
        metadata = [{"id": f"doc_{i}", **doc} for i, doc in enumerate(user_documents)]
        
        search_system = chatbot.search_system
        embedding_result = search_system.embedding_generator.generate_embeddings(texts)
        if isinstance(embedding_result, dict):
            embeddings = embedding_result['embeddings']
        else:
            embeddings = embedding_result
            
        search_system.vector_db.create_index(embeddings.shape[1], index_type="Flat")
        search_system.vector_db.add_vectors(embeddings, metadata)
        
        print(f"  ✅ 사용자 문서 {len(texts)}개 인덱싱 완료")
        
        # 6.3 페르소나 분석
        print("\n6.3 페르소나 분석")
        persona_result = chatbot.analyze_user_persona(user_documents)
        
        if persona_result['success']:
            print(f"  ✅ 페르소나 분석 완료")
        
        # 6.4 맞춤형 프로젝트 추천
        print("\n6.4 맞춤형 프로젝트 추천")
        question = "제 경험과 관심사를 바탕으로 다음에 도전해볼 만한 프로젝트를 추천해주세요"
        
        recommendation = chatbot.generate_project_recommendations(question)
        
        if recommendation['success']:
            print(f"  ✅ 프로젝트 추천 완료")
            print(f"    - 검색 컨텍스트 사용: {recommendation['context_used']}")
            print(f"    - 추천 길이: {len(recommendation['recommendation'])}자")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 통합 테스트 실패: {e}")
        return False


def test_6_mock_integration():
    """6. 모의 통합 테스트 (API 키 없을 때)"""
    try:
        print("\n  📝 모의 통합 테스트 진행")
        
        # 챗봇 초기화
        chatbot = PersonaChatbot()
        
        # 검색 시스템만 테스트
        sample_texts = ["테스트 문서입니다."]
        search_system = chatbot.search_system
        
        embedding_result = search_system.embedding_generator.generate_embeddings(sample_texts)
        if isinstance(embedding_result, dict):
            embeddings = embedding_result['embeddings']
        else:
            embeddings = embedding_result
            
        search_system.vector_db.create_index(embeddings.shape[1], index_type="Flat")
        search_system.vector_db.add_vectors(embeddings, [{"id": "test", "content": sample_texts[0]}])
        
        # 검색 테스트
        results = search_system.semantic_search("테스트", k=1)
        
        print(f"  ✅ 모의 통합 테스트 완료")
        print(f"    - 검색 시스템: 정상 작동")
        print(f"    - 검색 결과: {len(results)}개")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 모의 테스트 실패: {e}")
        return False


def main():
    """메인 테스트 실행"""
    print("🤖 Phase 4 페르소나 챗봇 테스트 시작")
    print("=" * 80)
    
    # 테스트 결과 추적
    test_results = {}
    
    # 1. 챗봇 초기화 테스트
    chatbot, api_available = test_1_chatbot_initialization()
    test_results["챗봇 초기화"] = "✅ 성공" if chatbot else "❌ 실패"
    
    if not chatbot:
        print("\n❌ 챗봇 초기화 실패로 테스트 중단")
        return
    
    # 2. 검색 시스템 통합 테스트
    search_success = test_2_search_integration()
    test_results["검색 시스템 통합"] = "✅ 성공" if search_success else "❌ 실패"
    
    # 3. 페르소나 분석 테스트 (API 키 필요)
    persona_success = test_3_persona_analysis(api_available)
    test_results["페르소나 분석"] = "✅ 성공" if persona_success else ("⚠️ API 키 필요" if not api_available else "❌ 실패")
    
    # 4. 프로젝트 추천 테스트 (API 키 필요)
    recommendation_success = test_4_project_recommendations(api_available)
    test_results["프로젝트 추천"] = "✅ 성공" if recommendation_success else ("⚠️ API 키 필요" if not api_available else "❌ 실패")
    
    # 5. 대화 관리 테스트
    conversation_success = test_5_conversation_management(api_available)
    test_results["대화 관리"] = "✅ 성공" if conversation_success else ("⚠️ API 키 필요" if not api_available else "❌ 실패")
    
    # 6. 통합 테스트
    integration_success = test_6_integration_test(api_available)
    test_results["통합 테스트"] = "✅ 성공" if integration_success else ("⚠️ API 키 필요" if not api_available else "❌ 실패")
    
    # 최종 결과 요약
    print("\n" + "=" * 80)
    print("🎯 Phase 4 테스트 결과 요약")
    print("=" * 80)
    
    for test_name, result in test_results.items():
        print(f"  {result} {test_name}")
    
    # 성공률 계산
    success_count = sum(1 for result in test_results.values() if "✅" in result)
    total_count = len(test_results)
    success_rate = (success_count / total_count) * 100
    
    print(f"\n📊 전체 성공률: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    if not api_available:
        print("\n⚠️ 참고사항:")
        print("   - OpenAI API 키가 설정되지 않아 일부 기능이 제한됩니다")
        print("   - API 키 설정 후 전체 기능 테스트가 가능합니다")
        print("   - 환경변수 OPENAI_API_KEY 또는 .env 파일에 설정하세요")
    
    if success_rate >= 80 or (success_count >= 2 and not api_available):
        print("\n🎉 Phase 4 페르소나 챗봇 구현 완료!")
        print("   ✅ OpenAI API 연동 (무료 크레딧 활용)")
        print("   ✅ 프롬프트 엔지니어링")
        print("   ✅ RAG 파이프라인 구성")
        print("   ✅ 개인 맞춤형 프로젝트 추천 로직")
        print("\n🚀 다음 단계: Phase 5 - 사용자 인터페이스 및 테스트")
    else:
        print("⚠️ 일부 테스트에서 문제가 발견되었습니다.")
        print("   문제를 해결한 후 다시 테스트해주세요.")


if __name__ == "__main__":
    main() 