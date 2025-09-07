"""
테스트에서 사용하는 실제 텍스트들로 디버깅
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.embedding_generator import EmbeddingGenerator

def test_specific_texts():
    """테스트에서 사용하는 실제 텍스트들로 테스트"""
    print("🔍 실제 테스트 텍스트들로 디버깅")
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
        print("📥 EmbeddingGenerator 생성...")
        embedding_gen = EmbeddingGenerator()
        
        print(f"📝 {len(texts)}개 실제 텍스트로 임베딩 생성...")
        for i, text in enumerate(texts):
            print(f"  텍스트 {i+1}: '{text}'")
        
        print("\n🔄 임베딩 생성 시작...")
        result = embedding_gen.generate_embeddings(texts)
        
        print(f"✅ 임베딩 생성 성공!")
        print(f"  - 형태: {result['embeddings'].shape}")
        print(f"  - 차원: {result['embedding_dim']}")
        print(f"  - 청크 수: {result['chunk_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 실제 텍스트 테스트 실패: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_specific_texts()
    print(f"\n🎯 결과: {'✅ 성공' if success else '❌ 실패'}") 