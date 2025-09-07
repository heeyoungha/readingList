"""
모델 추론 문제 디버깅
"""
import sys
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModel
from loguru import logger

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_model_directly():
    """모델을 직접 테스트"""
    print("🧠 모델 직접 테스트 시작...")
    
    try:
        # 모델 로드
        model_name = "klue/roberta-base"
        print(f"📥 모델 로딩: {model_name}")
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        device = torch.device("cpu")
        model.to(device)
        model.eval()
        
        print(f"✅ 모델 로드 완료")
        
        # 간단한 텍스트로 테스트
        test_text = "안녕하세요"
        print(f"📝 테스트 텍스트: '{test_text}'")
        
        # 토크나이징
        print("🔄 토크나이징...")
        inputs = tokenizer(
            test_text,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True
        )
        print(f"✅ 토크나이징 완료: {inputs['input_ids'].shape}")
        
        # 디바이스로 이동
        print("📱 디바이스로 이동...")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        print("✅ 디바이스 이동 완료")
        
        # 모델 추론
        print("🧠 모델 추론 시작...")
        with torch.no_grad():
            outputs = model(**inputs)
            print(f"✅ 모델 추론 완료: {outputs.last_hidden_state.shape}")
        
        print("🎉 모델 테스트 성공!")
        return True
        
    except Exception as e:
        print(f"❌ 모델 테스트 실패: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return False

def test_embedding_generator():
    """EmbeddingGenerator 클래스 테스트"""
    print("\n" + "="*50)
    print("🔧 EmbeddingGenerator 클래스 테스트")
    print("="*50)
    
    try:
        from utils.embedding_generator import EmbeddingGenerator
        
        print("📥 EmbeddingGenerator 생성...")
        embedding_gen = EmbeddingGenerator()
        
        print("📝 간단한 텍스트로 임베딩 생성...")
        test_texts = ["안녕하세요", "테스트입니다"]
        
        result = embedding_gen.generate_embeddings(test_texts)
        print(f"✅ 임베딩 생성 성공: {result['embeddings'].shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ EmbeddingGenerator 테스트 실패: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🔍 모델 추론 문제 디버깅 시작")
    print("="*60)
    
    # 1. 모델 직접 테스트
    success1 = test_model_directly()
    
    # 2. EmbeddingGenerator 테스트
    if success1:
        success2 = test_embedding_generator()
    else:
        print("❌ 모델 직접 테스트 실패로 EmbeddingGenerator 테스트 건너뜀")
        success2 = False
    
    print("\n" + "="*60)
    print("🎯 디버깅 결과 요약")
    print("="*60)
    print(f"모델 직접 테스트: {'✅ 성공' if success1 else '❌ 실패'}")
    print(f"EmbeddingGenerator 테스트: {'✅ 성공' if success2 else '❌ 실패'}") 