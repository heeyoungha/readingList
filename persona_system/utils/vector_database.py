"""
FAISS 벡터 데이터베이스 관리
"""
import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss
from loguru import logger


class VectorDatabase:
    """FAISS 벡터 데이터베이스 관리 클래스"""
    
    def __init__(self, index_path: str = "./data/faiss_index"):
        """
        벡터 데이터베이스 초기화
        
        Args:
            index_path: FAISS 인덱스 저장 경로
        """
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        self.index = None
        self.metadata = {}
        self.is_trained = False
        
        logger.info(f"벡터 데이터베이스 초기화: {index_path}")
    
    def create_index(self, embedding_dim: int, index_type: str = "IVFFlat") -> None:
        """
        FAISS 인덱스 생성
        
        Args:
            embedding_dim: 임베딩 차원
            index_type: 인덱스 타입 ("IVFFlat", "Flat", "HNSW")
        """
        logger.info(f"FAISS 인덱스 생성: {index_type}, 차원: {embedding_dim}")
        
        if index_type == "IVFFlat":
            # IVF (Inverted File Index) + Flat
            # 클러스터 수를 벡터 개수에 맞게 조정
            nlist = min(10, max(1, embedding_dim // 100))  # 클러스터 수를 줄임
            quantizer = faiss.IndexFlatIP(embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, embedding_dim, nlist, faiss.METRIC_INNER_PRODUCT)
            self.index.nprobe = min(5, nlist)  # 검색 시 탐색할 클러스터 수
            
        elif index_type == "Flat":
            # Flat (정확한 검색, 메모리 사용량 많음)
            self.index = faiss.IndexFlatIP(embedding_dim)
            
        elif index_type == "HNSW":
            # HNSW (Hierarchical Navigable Small World, 빠른 근사 검색)
            self.index = faiss.IndexHNSWFlat(embedding_dim, 32)  # 32는 각 노드의 최대 이웃 수
            self.index.hnsw.efConstruction = 200  # 인덱스 구축 시 탐색 깊이
            self.index.hnsw.efSearch = 100  # 검색 시 탐색 깊이
            
        else:
            raise ValueError(f"지원하지 않는 인덱스 타입: {index_type}")
        
        logger.info(f"인덱스 생성 완료: {type(self.index).__name__}")
    
    def add_vectors(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """
        벡터를 인덱스에 추가
        
        Args:
            embeddings: 추가할 임베딩 벡터 (numpy array)
            metadata: 각 벡터의 메타데이터
        """
        if self.index is None:
            raise ValueError("인덱스가 생성되지 않았습니다. create_index()를 먼저 호출하세요.")
        
        if len(embeddings) != len(metadata):
            raise ValueError("임베딩과 메타데이터의 개수가 일치하지 않습니다.")
        
        logger.info(f"벡터 추가 시작: {len(embeddings)}개")
        
        # 벡터 정규화 (코사인 유사도 계산을 위해)
        faiss.normalize_L2(embeddings)
        
        # 인덱스에 벡터 추가
        if hasattr(self.index, 'is_trained') and not self.index.is_trained:
            # IVF 인덱스의 경우 훈련 필요
            logger.info("인덱스 훈련 중...")
            self.index.train(embeddings)
            self.is_trained = True
            logger.info("인덱스 훈련 완료")
        
        # 벡터 추가
        self.index.add(embeddings)
        
        # 메타데이터 저장
        self.metadata = metadata
        
        logger.info(f"벡터 추가 완료: 총 {self.index.ntotal}개")
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """
        유사한 벡터 검색
        
        Args:
            query_vector: 검색할 쿼리 벡터
            k: 반환할 상위 k개 결과
        
        Returns:
            (거리, 인덱스, 메타데이터) 튜플
        """
        if self.index is None:
            raise ValueError("인덱스가 생성되지 않았습니다.")
        
        if self.index.ntotal == 0:
            logger.warning("인덱스에 벡터가 없습니다.")
            return np.array([]), np.array([]), []
        
        # 쿼리 벡터 정규화
        query_vector = query_vector.reshape(1, -1)
        faiss.normalize_L2(query_vector)
        
        # 검색 실행
        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
        
        # 결과 메타데이터 추출
        results_metadata = []
        for idx in indices[0]:
            if idx != -1:  # -1은 유효하지 않은 인덱스
                results_metadata.append(self.metadata[idx])
        
        logger.info(f"검색 완료: {len(results_metadata)}개 결과")
        
        return distances[0], indices[0], results_metadata
    
    def search_by_text(self, query_text: str, k: int = 5, embedding_generator=None) -> List[Dict[str, Any]]:
        """
        텍스트로 유사한 벡터 검색
        
        Args:
            query_text: 검색할 텍스트
            k: 반환할 상위 k개 결과
            embedding_generator: 임베딩 생성기
        
        Returns:
            검색 결과 메타데이터 리스트
        """
        if embedding_generator is None:
            raise ValueError("embedding_generator가 필요합니다.")
        
        # 텍스트를 임베딩으로 변환
        query_embedding = embedding_generator.model.encode([query_text], normalize_embeddings=True)[0]
        
        # 검색 실행
        distances, indices, metadata = self.search(query_embedding, k)
        
        # 거리 정보 추가
        for i, meta in enumerate(metadata):
            meta['similarity_score'] = float(distances[i])
            meta['rank'] = i + 1
        
        return metadata
    
    def batch_search(self, query_vectors: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray, List[List[Dict[str, Any]]]]:
        """
        여러 쿼리 벡터에 대한 배치 검색
        
        Args:
            query_vectors: 검색할 쿼리 벡터들 (numpy array)
            k: 각 쿼리당 반환할 상위 k개 결과
        
        Returns:
            (거리, 인덱스, 메타데이터) 튜플
        """
        if self.index is None:
            raise ValueError("인덱스가 생성되지 않았습니다.")
        
        # 쿼리 벡터 정규화
        faiss.normalize_L2(query_vectors)
        
        # 배치 검색 실행
        distances, indices = self.index.search(query_vectors, min(k, self.index.ntotal))
        
        # 결과 메타데이터 추출
        all_results_metadata = []
        for query_idx in range(len(query_vectors)):
            query_results = []
            for rank_idx, idx in enumerate(indices[query_idx]):
                if idx != -1:
                    meta = self.metadata[idx].copy()
                    meta['similarity_score'] = float(distances[query_idx][rank_idx])
                    meta['rank'] = rank_idx + 1
                    query_results.append(meta)
            all_results_metadata.append(query_results)
        
        logger.info(f"배치 검색 완료: {len(query_vectors)}개 쿼리, 각각 {k}개 결과")
        
        return distances, indices, all_results_metadata
    
    def save_index(self, save_path: Optional[str] = None) -> None:
        """
        FAISS 인덱스와 메타데이터 저장
        
        Args:
            save_path: 저장 경로 (None이면 기본 경로 사용)
        """
        if save_path is None:
            save_path = self.index_path / "faiss_index"
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # FAISS 인덱스 저장
        index_path = save_path.with_suffix('.faiss')
        faiss.write_index(self.index, str(index_path))
        
        # 메타데이터 저장
        metadata_path = save_path.with_suffix('.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': self.metadata,
                'total_vectors': self.index.ntotal if self.index else 0,
                'is_trained': self.is_trained,
                'index_type': type(self.index).__name__ if self.index else None
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"인덱스 저장 완료: {save_path}")
        logger.info(f"  - FAISS 인덱스: {index_path}")
        logger.info(f"  - 메타데이터: {metadata_path}")
    
    def load_index(self, load_path: Optional[str] = None) -> None:
        """
        저장된 FAISS 인덱스와 메타데이터 로드
        
        Args:
            load_path: 로드할 파일 경로 (None이면 기본 경로 사용)
        """
        if load_path is None:
            load_path = self.index_path / "faiss_index"
        
        load_path = Path(load_path)
        
        # FAISS 인덱스 로드
        index_path = load_path.with_suffix('.faiss')
        if not index_path.exists():
            raise FileNotFoundError(f"FAISS 인덱스 파일을 찾을 수 없습니다: {index_path}")
        
        self.index = faiss.read_index(str(index_path))
        
        # 메타데이터 로드
        metadata_path = load_path.with_suffix('.json')
        if not metadata_path.exists():
            raise FileNotFoundError(f"메타데이터 파일을 찾을 수 없습니다: {metadata_path}")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.metadata = data['metadata']
            self.is_trained = data.get('is_trained', False)
        
        logger.info(f"인덱스 로드 완료: {load_path}")
        logger.info(f"  - 총 벡터 수: {self.index.ntotal}")
        logger.info(f"  - 인덱스 타입: {type(self.index).__name__}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        인덱스 통계 정보 반환
        
        Returns:
            인덱스 통계 정보
        """
        if self.index is None:
            return {
                'status': 'not_initialized',
                'total_vectors': 0,
                'index_type': None
            }
        
        stats = {
            'status': 'ready',
            'total_vectors': self.index.ntotal,
            'index_type': type(self.index).__name__,
            'is_trained': self.is_trained,
            'metadata_count': len(self.metadata)
        }
        
        # IVF 인덱스 특별 정보
        if hasattr(self.index, 'nlist'):
            stats['nlist'] = self.index.nlist
            stats['nprobe'] = self.index.nprobe
        
        # HNSW 인덱스 특별 정보
        if hasattr(self.index, 'hnsw'):
            stats['ef_construction'] = self.index.hnsw.efConstruction
            stats['ef_search'] = self.index.hnsw.efSearch
        
        return stats
    
    def clear_index(self) -> None:
        """인덱스 초기화"""
        if self.index:
            self.index.reset()
            self.metadata = []
            self.is_trained = False
            logger.info("인덱스 초기화 완료")
    
    def delete_vectors(self, indices: List[int]) -> None:
        """
        특정 벡터 삭제 (제한적 지원)
        
        Args:
            indices: 삭제할 벡터의 인덱스 리스트
        """
        if not hasattr(self.index, 'remove_ids'):
            logger.warning("이 인덱스 타입은 벡터 삭제를 지원하지 않습니다.")
            return
        
        # FAISS 인덱스에서 벡터 삭제
        self.index.remove_ids(np.array(indices))
        
        # 메타데이터에서도 삭제
        for idx in sorted(indices, reverse=True):
            if idx < len(self.metadata):
                del self.metadata[idx]
        
        logger.info(f"벡터 삭제 완료: {len(indices)}개")
    
    def get_supabase_migration_info(self) -> Dict[str, Any]:
        """
        Supabase 전환을 위한 정보 반환
        
        Returns:
            전환 정보
        """
        return {
            'current_status': 'local_faiss',
            'migration_target': 'supabase_vector_extension',
            'migration_benefits': [
                'Vercel 배포 호환',
                '사용자별 데이터 격리',
                '실시간 데이터 동기화',
                '자동 백업 및 모니터링'
            ],
            'migration_steps': [
                '1. Supabase 프로젝트 생성',
                '2. pgvector 확장 설치',
                '3. 사용자별 임베딩 테이블 생성',
                '4. 기존 FAISS 데이터 마이그레이션',
                '5. 벡터 검색 함수 구현',
                '6. Vercel API Routes 연동'
            ],
            'table_schema_example': {
                'user_embeddings': {
                    'id': 'UUID PRIMARY KEY',
                    'user_id': 'UUID REFERENCES auth.users(id)',
                    'embedding_vector': 'vector(768)',
                    'chunk_text': 'TEXT',
                    'chunk_metadata': 'JSONB',
                    'text_source': 'VARCHAR(100)',
                    'source_id': 'UUID',
                    'created_at': 'TIMESTAMP'
                }
            },
            'estimated_migration_time': '2-3일',
            'current_functionality': '로컬 FAISS 완벽 지원',
            'future_functionality': 'Supabase + Vercel 완벽 호환'
        }
    
    def export_to_supabase_format(self) -> Dict[str, Any]:
        """
        Supabase 전환을 위한 데이터 형식 내보내기
        
        Returns:
            Supabase 호환 데이터 형식
        """
        if not self.index or self.index.ntotal == 0:
            return {
                'status': 'no_data',
                'message': '내보낼 데이터가 없습니다.'
            }
        
        # 현재 FAISS 데이터를 Supabase 형식으로 변환
        supabase_data = []
        
        for i, meta in enumerate(self.metadata):
            if self.index:
                # 벡터 데이터 추출 (numpy array를 list로 변환)
                vector_data = self.index.reconstruct(i).tolist()
                
                supabase_record = {
                    'embedding_vector': vector_data,
                    'chunk_text': meta.get('text', ''),
                    'chunk_metadata': meta,
                    'text_source': meta.get('text_source', 'unknown'),
                    'source_id': meta.get('source_id', None),
                    'word_count': meta.get('word_count', 0),
                    'char_count': meta.get('char_count', 0)
                }
                supabase_data.append(supabase_record)
        
        return {
            'status': 'success',
            'total_records': len(supabase_data),
            'data_format': 'supabase_compatible',
            'sample_record': supabase_data[0] if supabase_data else None,
            'migration_ready': True,
            'estimated_storage_size': f"{len(supabase_data) * 768 * 4 / 1024 / 1024:.2f} MB"
        } 