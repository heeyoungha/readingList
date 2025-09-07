"""
SearchSystem을 통한 임베딩 생성 디버깅
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.search_system import SearchSystem

def test_search_system_embedding():
    """SearchSystem을 통한 임베딩 생성 테스트"""
    print("🔍 SearchSystem을 통한 임베딩 생성 디버깅")
    print("="*60)
    
    # 테스트에서 사용하는 실제 텍스트들
    sample_data = [
        {"content": "Python을 이용한 데이터 분석 프로젝트를 진행했습니다. 판다스와 넘파이를 활용하여 데이터를 처리하고 시각화했습니다.", "type": "project"},
        {"content": "감정 분석 알고리즘을 구현하여 텍스트의 긍정/부정을 판단하는 모델을 만들었습니다.", "type": "project"},
        {"content": "이 책을 읽고 창의적 사고의 중요성을 깨달았습니다. 다양한 관점에서 문제를 바라보는 능력이 중요합니다.", "type": "review"},
        {"content": "머신러닝 스터디를 통해 다양한 알고리즘을 학습했습니다. 선형회귀부터 신경망까지 폭넓게 다뤘습니다.", "type": "study"},
        {"content": "글쓰기 워크샵에서 스토리텔링 기법을 배웠습니다. 독자의 관심을 끄는 방법을 익혔습니다.", "type": "workshop"}
    ]
    
    texts = [item["content"] for item in sample_data]
    
    try:
        print("📥 SearchSystem 생성...")
        search_system = SearchSystem()
        
        print(f"📝 SearchSystem을 통해 {len(texts)}개 텍스트로 임베딩 생성...")
        
        # SearchSystem의 embedding_generator 직접 사용
        print("\n🔄 SearchSystem.embedding_generator로 임베딩 생성...")
        embedding_result = search_system.embedding_generator.generate_embeddings(texts)
        
        # 결과가 dict 형태인지 numpy 배열인지 확인
        if isinstance(embedding_result, dict):
            embeddings = embedding_result['embeddings']
        else:
            embeddings = embedding_result
            
        print(f"✅ SearchSystem을 통한 임베딩 생성 성공!")
        print(f"  - 형태: {embeddings.shape}")
        print(f"  - 타입: {type(embeddings)}")
        
        # 벡터 DB 테스트
        print("\n🔄 벡터 DB 인덱스 생성...")
        search_system.vector_db.create_index(embeddings.shape[1], index_type="Flat")
        
        sample_metadata = []
        for i, item in enumerate(sample_data):
            metadata = {
                'id': f'doc_{i}',
                **item
            }
            sample_metadata.append(metadata)
        
        print("🔄 벡터 DB에 추가...")
        search_system.vector_db.add_vectors(embeddings, sample_metadata)
        
        print("✅ 벡터 DB 구축 완료!")
        
        return True
        
    except Exception as e:
        print(f"❌ SearchSystem 테스트 실패: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_search_system_embedding()
    print(f"\n🎯 결과: {'✅ 성공' if success else '❌ 실패'}") 