"""
텍스트 임베딩 생성 및 관리
"""
import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

# sentence-transformers 대신 transformers 직접 사용
from transformers import AutoTokenizer, AutoModel
import torch


class EmbeddingGenerator:
    """텍스트 임베딩 생성기 (transformers 직접 사용)"""
    
    def __init__(self, model_name: str = "klue/roberta-base"):
        """
        임베딩 생성기 초기화
        
        Args:
            model_name: 사용할 모델명 (기본값: klue/roberta-base)
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        logger.info(f"임베딩 생성기 초기화: {model_name}")
        logger.info(f"  - 현재 지원: ['local']")
        logger.info(f"  - 향후 지원: ['supabase', 's3', 'hybrid']")
        logger.info(f"  - 현재 단계: Phase 2 - 로컬 FAISS 완료")
        logger.info(f"  - 다음 단계: Phase 3 - 검색 시스템 구현 (로컬 FAISS)")
        logger.info(f"  - 전환 단계: Phase 4 이후 - Supabase 전환")
        
        # 모델 로딩 시도
        self.load_model()
    
    def load_model(self) -> None:
        """transformers 모델 로드 (PyTorch 2.2.2 호환)"""
        try:
            logger.info("모델 로딩 중...")
            
            # PyTorch 버전 체크
            torch_version = torch.__version__
            logger.info(f"PyTorch 버전: {torch_version}")
            
            # 더 호환성 좋은 한국어 모델 사용
            if "klue" in self.model_name or "beomi" in self.model_name:
                logger.info("한국어 전용 모델 사용")
            else:
                logger.info("범용 모델 사용")
            
            # 토크나이저와 모델 로드
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            
            # 모델을 평가 모드로 설정하고 디바이스로 이동
            self.model.eval()
            self.model.to(self.device)
            
            logger.info(f"모델 로드 완료: {self.model_name}")
            logger.info(f"사용 디바이스: {self.device}")
            
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            
            # 대체 모델 시도
            logger.info("대체 모델로 시도...")
            try:
                # 더 가벼운 한국어 모델 시도
                fallback_model = "beomi/kcbert-base"
                logger.info(f"대체 모델 시도: {fallback_model}")
                
                self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
                self.model = AutoModel.from_pretrained(fallback_model)
                
                self.model.eval()
                self.model.to(self.device)
                
                self.model_name = fallback_model
                logger.info("대체 모델 로드 성공")
                
            except Exception as e2:
                logger.error(f"대체 모델도 실패: {e2}")
                raise
    
    def generate_embeddings(self, texts: List[str]) -> Dict[str, Any]:
        """
        텍스트 리스트로부터 임베딩 생성
        
        Args:
            texts: 임베딩을 생성할 텍스트 리스트
            
        Returns:
            임베딩 데이터 딕셔너리
        """
        if self.model is None or self.tokenizer is None:
            raise ValueError("모델이 로드되지 않았습니다.")
        
        logger.info(f"임베딩 생성 시작: {len(texts)}개 텍스트")
        
        embeddings = []
        chunks = []
        
        for i, text in enumerate(texts):
            try:
                # 텍스트 전처리
                if not text or not text.strip():
                    continue
                
                # 토크나이징
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    max_length=512,
                    truncation=True,
                    padding=True
                )
                
                # 디바이스로 이동
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # 임베딩 생성 (그래디언트 계산 비활성화)
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    # [CLS] 토큰의 임베딩 사용 (문장 전체 표현)
                    embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                    embeddings.append(embedding.flatten())
                    chunks.append(text)
                
                logger.debug(f"텍스트 {i+1}/{len(texts)} 임베딩 생성 완료")
                
            except Exception as e:
                logger.error(f"❌ 텍스트 {i+1} 임베딩 생성 실패: {e}")
                import traceback
                logger.error(f"상세 오류: {traceback.format_exc()}")
                continue
        
        if not embeddings:
            raise ValueError("모든 텍스트의 임베딩 생성에 실패했습니다.")
        
        # NumPy 배열로 변환
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        logger.info(f"임베딩 생성 완료: {len(embeddings_array)}개, 차원: {embeddings_array.shape[1]}")
        
        return {
            'embeddings': embeddings_array,
            'chunks': chunks,
            'model_name': self.model_name,
            'embedding_dim': embeddings_array.shape[1],
            'chunk_count': len(chunks)
        }
    
    def save_embeddings(self, embeddings_data: Dict[str, Any], save_path: str, storage_type: str = "local", user_id: str = None) -> None:
        """
        임베딩 데이터 저장
        
        Args:
            embeddings_data: 저장할 임베딩 데이터
            save_path: 저장 경로
            storage_type: 저장소 타입 (현재는 local만 지원)
            user_id: 사용자 ID (향후 확장용)
        """
        if storage_type == "local":
            self._save_local_embeddings(embeddings_data, save_path, user_id)
        else:
            logger.warning(f"저장소 타입 '{storage_type}'은 아직 지원되지 않습니다. 로컬 저장을 사용합니다.")
            self._save_local_embeddings(embeddings_data, save_path, user_id)
    
    def _save_local_embeddings(self, embeddings_data: Dict[str, Any], save_path: str, user_id: str = None) -> None:
        """로컬 파일 시스템에 임베딩 저장"""
        try:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 임베딩 벡터 저장 (.npy)
            embeddings_path = save_path.with_suffix('.npy')
            np.save(embeddings_path, embeddings_data['embeddings'])
            
            # 메타데이터 저장 (.json)
            metadata = {
                'chunks': embeddings_data['chunks'],
                'model_name': embeddings_data['model_name'],
                'embedding_dim': embeddings_data['embedding_dim'],
                'chunk_count': embeddings_data['chunk_count'],
                'created_at': datetime.now().isoformat(),
                'storage_type': 'local',
                'user_id': user_id
            }
            
            metadata_path = save_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"임베딩 저장 완료: {embeddings_path}, {metadata_path}")
            
        except Exception as e:
            logger.error(f"임베딩 저장 실패: {e}")
            raise
    
    def load_embeddings(self, load_path: str, storage_type: str = "local") -> Dict[str, Any]:
        """
        임베딩 데이터 로드
        
        Args:
            load_path: 로드할 파일 경로
            storage_type: 저장소 타입 (현재는 local만 지원)
            
        Returns:
            로드된 임베딩 데이터
        """
        if storage_type == "local":
            return self._load_local_embeddings(load_path)
        else:
            logger.warning(f"저장소 타입 '{storage_type}'은 아직 지원되지 않습니다. 로컬 로드를 사용합니다.")
            return self._load_local_embeddings(load_path)
    
    def _load_local_embeddings(self, load_path: str) -> Dict[str, Any]:
        """로컬 파일 시스템에서 임베딩 로드"""
        try:
            load_path = Path(load_path)
            
            # 임베딩 벡터 로드 (.npy)
            embeddings_path = load_path.with_suffix('.npy')
            embeddings = np.load(embeddings_path)
            
            # 메타데이터 로드 (.json)
            metadata_path = load_path.with_suffix('.json')
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 데이터 통합
            result = {
                'embeddings': embeddings,
                'chunks': metadata['chunks'],
                'model_name': metadata['model_name'],
                'embedding_dim': metadata['embedding_dim'],
                'chunk_count': metadata['chunk_count'],
                'created_at': metadata.get('created_at'),
                'storage_type': metadata.get('storage_type', 'local')
            }
            
            logger.info(f"임베딩 로드 완료: {embeddings_path}, {metadata_path}")
            return result
            
        except Exception as e:
            logger.error(f"임베딩 로드 실패: {e}")
            raise
    
    def get_storage_info(self) -> Dict[str, List[str]]:
        """지원되는 저장소 타입 정보 반환"""
        return {
            'current': ['local'],
            'planned': ['supabase', 's3', 'hybrid']
        }
    
    def validate_storage_type(self, storage_type: str) -> bool:
        """저장소 타입 유효성 검증"""
        valid_types = ['local', 'supabase', 's3', 'hybrid']
        return storage_type in valid_types
    
    # 향후 Supabase 전환을 위한 플레이스홀더 메서드들
    def save_embeddings_to_supabase(self, embeddings_data: Dict[str, Any], user_id: str) -> None:
        """Supabase에 임베딩 저장 (향후 구현)"""
        logger.info("Supabase 저장 기능은 향후 구현 예정입니다.")
        # TODO: Supabase 벡터 확장을 사용한 저장 구현
    
    def load_embeddings_from_supabase(self, user_id: str) -> Dict[str, Any]:
        """Supabase에서 임베딩 로드 (향후 구현)"""
        logger.info("Supabase 로드 기능은 향후 구현 예정입니다.")
        # TODO: Supabase 벡터 확장을 사용한 로드 구현
    
    def get_supabase_migration_plan(self) -> Dict[str, str]:
        """Supabase 전환 계획 반환"""
        return {
            'current': 'local_file_storage',
            'target': 'supabase_vector_extension',
            'method': 'pgvector_migration',
            'timeline': 'Phase_4_after_search_system'
        } 