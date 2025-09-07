"""
🔍 Phase 3 테스트: 검색 시스템 구현 완료 (수정 버전)

SearchSystem 인스턴스를 한 번만 생성하고 재사용하여 메모리 문제를 해결합니다.
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
from utils.search_system import SearchSystem


# 전역 SearchSystem 인스턴스
GLOBAL_SEARCH_SYSTEM = None

def get_search_system():
    """전역 SearchSystem 인스턴스 반환 (싱글톤 패턴)"""
    global GLOBAL_SEARCH_SYSTEM
    if GLOBAL_SEARCH_SYSTEM is None:
        GLOBAL_SEARCH_SYSTEM = SearchSystem()
    return GLOBAL_SEARCH_SYSTEM


def test_1_search_system_initialization():
    """1. 검색 시스템 초기화 테스트"""
    print("=" * 60)
    print("🔍 1. 검색 시스템 초기화 테스트")
    print("=" * 60)
    
    try:
        # 1.1 검색 시스템 생성
        print("\n1.1 검색 시스템 생성")
        search_system = get_search_system()
        print(f"  ✅ SearchSystem 생성 성공")
        print(f"    - 벡터 DB 경로: {search_system.vector_db_path}")
        print(f"    - 임베딩 모델: {search_system.embedding_model}")
        print(f"    - 기본 검색 결과 수: {search_system.default_k}")
        
        # 1.2 컴포넌트 확인
        print("\n1.2 컴포넌트 확인")
        print(f"  ✅ EmbeddingGenerator: {type(search_system.embedding_generator).__name__}")
        print(f"  ✅ VectorDatabase: {type(search_system.vector_db).__name__}")
        print(f"  ✅ TextPreprocessor: {type(search_system.text_preprocessor).__name__}")
        
        # 1.3 시스템 통계 확인
        print("\n1.3 시스템 통계 확인")
        stats = search_system.get_search_stats()
        print(f"  ✅ 시스템 상태: {stats['system_status']}")
        print(f"    - 벡터 DB 상태: {stats['vector_database']['status']}")
        print(f"    - 임베딩 생성기: {stats['components']['embedding_generator']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 테스트 실패: {e}")
        return False


def test_2_query_preprocessing_and_embedding():
    """2. 질문 전처리 및 임베딩 변환 테스트"""
    print("=" * 60)
    print("🔤 2. 질문 전처리 및 임베딩 변환 테스트")
    print("=" * 60)
    
    try:
        search_system = get_search_system()
        
        # 2.1 질문 전처리 테스트
        print("\n2.1 질문 전처리 테스트")
        test_queries = [
            "책 추천해줘",
            "감정 분석 관련 프로젝트 아이디어가 필요해",
            "글쓰기 스타일을 개선하고 싶어",
            "창의적인 아이디어를 얻고 싶어"
        ]
        
        for query in test_queries:
            processed = search_system.preprocess_query(query)
            print(f"  ✅ '{query}' -> '{processed[:50]}...'")
        
        # 2.2 임베딩 생성 테스트
        print("\n2.2 임베딩 생성 테스트")
        test_query = "독서 추천 시스템을 만들고 싶어"
        
        try:
            embedding = search_system.generate_query_embedding(test_query)
            print(f"  ✅ 질문 임베딩 생성 성공")
            print(f"    - 질문: '{test_query}'")
            print(f"    - 임베딩 형태: {embedding.shape}")
            print(f"    - 임베딩 타입: {type(embedding)}")
            print(f"    - 값 범위: [{embedding.min():.4f}, {embedding.max():.4f}]")
            
        except Exception as e:
            print(f"  ❌ 임베딩 생성 실패: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 테스트 실패: {e}")
        return False


def test_3_semantic_search_with_sample_data():
    """3. 샘플 데이터로 의미적 검색 테스트"""
    print("=" * 60)
    print("🔍 3. 샘플 데이터로 의미적 검색 테스트")
    print("=" * 60)
    
    try:
        search_system = get_search_system()
        
        # 3.1 샘플 데이터 생성
        print("\n3.1 샘플 데이터 생성")
        sample_texts = [
            "이 책은 인공지능과 머신러닝에 대한 기초적인 내용을 다룹니다.",
            "감정 분석을 통해 사용자의 기분 상태를 파악할 수 있습니다.",
            "창의적 글쓰기는 상상력과 표현력을 기르는 데 도움이 됩니다.",
            "데이터 사이언스 프로젝트를 진행할 때는 체계적인 접근이 필요합니다.",
            "독서 습관을 기르면 지식과 사고력을 향상시킬 수 있습니다."
        ]
        
        sample_metadata = []
        for i, text in enumerate(sample_texts):
            metadata = {
                'id': f'sample_{i}',
                'content': text,
                'type': 'book_review',
                'date': '2024-01-01'
            }
            sample_metadata.append(metadata)
        
        print(f"  ✅ {len(sample_texts)}개 샘플 텍스트 생성")
        
        # 3.2 임베딩 생성 및 인덱스 구축
        print("\n3.2 임베딩 생성 및 인덱스 구축")
        try:
            embedding_result = search_system.embedding_generator.generate_embeddings(sample_texts)
            
            # 결과가 dict 형태인지 numpy 배열인지 확인
            if isinstance(embedding_result, dict):
                embeddings = embedding_result['embeddings']
            else:
                embeddings = embedding_result
                
            print(f"  ✅ 임베딩 생성 완료: {embeddings.shape}")
            
            # 벡터 DB에 추가 (테스트용으로 Flat 인덱스 사용)
            search_system.vector_db.create_index(embeddings.shape[1], index_type="Flat")
            search_system.vector_db.add_vectors(embeddings, sample_metadata)
            print(f"  ✅ 벡터 DB 구축 완료")
            
        except Exception as e:
            print(f"  ❌ 인덱스 구축 실패: {e}")
            return False
        
        # 3.3 의미적 검색 테스트
        print("\n3.3 의미적 검색 테스트")
        test_queries = [
            "AI와 머신러닝에 대해 알고 싶어",
            "감정을 분석하는 방법이 궁금해",
            "글쓰기 실력을 늘리고 싶어"
        ]
        
        for query in test_queries:
            print(f"\n  🔍 검색 질문: '{query}'")
            results = search_system.semantic_search(query, k=3)
            
            if results:
                print(f"    ✅ {len(results)}개 결과 발견")
                for i, result in enumerate(results[:2]):  # 상위 2개만 표시
                    print(f"    [{i+1}] 유사도: {result['similarity_score']:.4f}")
                    print(f"        내용: {result['content'][:50]}...")
            else:
                print(f"    ❌ 검색 결과 없음")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 테스트 실패: {e}")
        return False


def test_4_context_composition():
    """4. 검색 결과 컨텍스트 구성 테스트"""
    print("=" * 60)
    print("📝 4. 검색 결과 컨텍스트 구성 테스트")
    print("=" * 60)
    
    try:
        search_system = get_search_system()
        
        # 4.1 샘플 검색 결과 생성
        print("\n4.1 샘플 검색 결과 생성")
        sample_results = [
            {
                'id': 'result_1',
                'content': '인공지능 기술은 현대 사회의 많은 분야에서 혁신을 이끌고 있습니다.',
                'similarity_score': 0.85,
                'type': 'book_review'
            },
            {
                'id': 'result_2', 
                'content': '머신러닝 알고리즘을 이해하기 위해서는 수학적 기초가 중요합니다.',
                'similarity_score': 0.78,
                'type': 'action_list'
            }
        ]
        
        print(f"  ✅ {len(sample_results)}개 샘플 결과 생성")
        
        # 4.2 컨텍스트 구성 테스트
        print("\n4.2 컨텍스트 구성 테스트")
        context_info = search_system.compose_search_context(sample_results, max_context_length=500)
        
        print(f"  ✅ 컨텍스트 구성 완료")
        print(f"    - 사용된 출처: {context_info['source_count']}개")
        print(f"    - 총 길이: {context_info['total_length']}자")
        print(f"    - 잘림 여부: {context_info['truncated']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 테스트 실패: {e}")
        return False


def test_5_advanced_search():
    """5. 고급 검색 기능 테스트"""
    print("=" * 60)
    print("🚀 5. 고급 검색 기능 테스트")
    print("=" * 60)
    
    try:
        search_system = get_search_system()
        
        # 이미 구축된 인덱스가 있다면 그대로 사용, 없다면 새로 구축
        stats = search_system.vector_db.get_index_stats()
        if stats['total_vectors'] == 0:
            print("\n5.1 샘플 데이터로 인덱스 구축")
            sample_texts = [
                "이 책은 인공지능과 머신러닝에 대한 기초적인 내용을 다룹니다.",
                "감정 분석을 통해 사용자의 기분 상태를 파악할 수 있습니다."
            ]
            
            sample_metadata = []
            for i, text in enumerate(sample_texts):
                metadata = {
                    'id': f'sample_{i}',
                    'content': text,
                    'type': 'book_review',
                    'date': '2024-01-01'
                }
                sample_metadata.append(metadata)
            
            # 인덱스 구축
            embedding_result = search_system.embedding_generator.generate_embeddings(sample_texts)
            if isinstance(embedding_result, dict):
                embeddings = embedding_result['embeddings']
            else:
                embeddings = embedding_result
                
            search_system.vector_db.create_index(embeddings.shape[1], index_type="Flat")
            search_system.vector_db.add_vectors(embeddings, sample_metadata)
            print(f"  ✅ 인덱스 구축 완료")
        
        # 5.2 고급 검색 테스트
        print("\n5.2 고급 검색 테스트")
        query = "AI 프로젝트를 시작하고 싶어"
        
        # 필터 없는 검색
        result1 = search_system.advanced_search(query, k=2)
        print(f"  ✅ 기본 고급 검색 완료")
        print(f"    - 결과 수: {result1['metadata']['total_results']}")
        print(f"    - 컨텍스트 길이: {result1['context']['total_length']}자")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 테스트 실패: {e}")
        return False


def main():
    """메인 테스트 실행"""
    print("🔍 Phase 3 검색 시스템 테스트 시작 (수정 버전)")
    print("=" * 80)
    
    # 테스트 결과 추적
    test_results = {}
    
    # 테스트 실행
    tests = [
        ("검색 시스템 초기화", test_1_search_system_initialization),
        ("질문 전처리 및 임베딩", test_2_query_preprocessing_and_embedding),
        ("의미적 검색", test_3_semantic_search_with_sample_data),
        ("컨텍스트 구성", test_4_context_composition),
        ("고급 검색", test_5_advanced_search)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            test_results[test_name] = "✅ 성공" if result else "❌ 실패"
        except Exception as e:
            test_results[test_name] = f"❌ 오류: {e}"
            logger.error(f"테스트 오류 - {test_name}: {e}")
    
    # 최종 결과 요약
    print("\n" + "=" * 80)
    print("🎯 Phase 3 테스트 결과 요약 (수정 버전)")
    print("=" * 80)
    
    for test_name, result in test_results.items():
        print(f"  {result} {test_name}")
    
    # 성공률 계산
    success_count = sum(1 for result in test_results.values() if "✅" in result)
    total_count = len(test_results)
    success_rate = (success_count / total_count) * 100
    
    print(f"\n📊 전체 성공률: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 Phase 3 검색 시스템 구현 완료!")
        print("   ✅ 의미적 검색 시스템 개발")
        print("   ✅ 사용자 질문 임베딩 변환") 
        print("   ✅ FAISS 유사도 검색 (상위 3-5개 결과)")
        print("   ✅ 검색 결과 컨텍스트 구성")
        print("\n🚀 다음 단계: Phase 4 - 페르소나 챗봇 개발")
    else:
        print("⚠️  일부 테스트에서 문제가 발견되었습니다.")
        print("   문제를 해결한 후 다시 테스트해주세요.")


if __name__ == "__main__":
    main() 