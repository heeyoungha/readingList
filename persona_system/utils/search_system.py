"""
🔍 Phase 3: 검색 시스템 구현

의미적 검색 시스템, 사용자 질문 임베딩 변환, FAISS 유사도 검색, 검색 결과 컨텍스트 구성
"""
import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
from loguru import logger

from .embedding_generator import EmbeddingGenerator
from .vector_database import VectorDatabase
from .text_preprocessor import TextPreprocessor


class SearchSystem:
    """Phase 3: 의미적 검색 시스템"""
    
    def __init__(self, 
                 vector_db_path: str = "./data/faiss_index",
                 embedding_model: str = "klue/roberta-base"):
        """
        검색 시스템 초기화
        
        Args:
            vector_db_path: 벡터 데이터베이스 경로
            embedding_model: 임베딩 모델명
        """
        self.vector_db_path = vector_db_path
        self.embedding_model = embedding_model
        
        # 컴포넌트 초기화
        self.embedding_generator = EmbeddingGenerator(model_name=embedding_model)
        self.vector_db = VectorDatabase(index_path=vector_db_path)
        self.text_preprocessor = TextPreprocessor()
        
        # 검색 설정
        self.default_k = 5  # 기본 검색 결과 수
        self.min_similarity_threshold = 0.3  # 최소 유사도 임계값
        
        logger.info("🔍 Phase 3 검색 시스템 초기화 완료")
        logger.info(f"  - 벡터 DB 경로: {vector_db_path}")
        logger.info(f"  - 임베딩 모델: {embedding_model}")
    
    def load_index(self, index_path: Optional[str] = None) -> bool:
        """
        저장된 FAISS 인덱스 로드
        
        Args:
            index_path: 인덱스 파일 경로
            
        Returns:
            로드 성공 여부
        """
        try:
            self.vector_db.load_index(index_path)
            logger.info("✅ FAISS 인덱스 로드 성공")
            return True
        except Exception as e:
            logger.error(f"❌ FAISS 인덱스 로드 실패: {e}")
            return False
    
    def preprocess_query(self, query: str) -> str:
        """
        사용자 질문 전처리
        
        Args:
            query: 원본 질문
            
        Returns:
            전처리된 질문
        """
        # 기본 전처리
        processed_query = self.text_preprocessor.clean_text(query)
        
        # 질문 확장 (선택적)
        # 예: "책 추천해줘" -> "책 추천 도서 독서 문학"
        expanded_query = self._expand_query(processed_query)
        
        logger.info(f"질문 전처리: '{query}' -> '{expanded_query}'")
        return expanded_query
    
    def _expand_query(self, query: str) -> str:
        """
        질문 확장 (동의어, 관련어 추가)
        
        Args:
            query: 전처리된 질문
            
        Returns:
            확장된 질문
        """
        # 간단한 키워드 확장 규칙
        expansion_rules = {
            "책": "도서 문학 독서",
            "추천": "제안 권장 소개",
            "감정": "기분 느낌 정서",
            "프로젝트": "과제 작업 계획",
            "아이디어": "생각 발상 창의",
            "글쓰기": "작문 문서 작성"
        }
        
        expanded_terms = []
        for keyword, synonyms in expansion_rules.items():
            if keyword in query:
                expanded_terms.extend(synonyms.split())
        
        if expanded_terms:
            return f"{query} {' '.join(expanded_terms)}"
        return query
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """
        사용자 질문을 임베딩으로 변환
        
        Args:
            query: 사용자 질문
            
        Returns:
            질문 임베딩 벡터
        """
        try:
            # 질문 전처리
            processed_query = self.preprocess_query(query)
            
            # 임베딩 생성
            embedding_result = self.embedding_generator.generate_embeddings([processed_query])
            
            # 결과가 dict 형태인지 numpy 배열인지 확인
            if isinstance(embedding_result, dict):
                embedding = embedding_result['embeddings'][0]
            else:
                embedding = embedding_result[0]
            
            logger.info(f"질문 임베딩 생성 완료: {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"질문 임베딩 생성 실패: {e}")
            raise
    
    def semantic_search(self, 
                       query: str, 
                       k: int = None,
                       similarity_threshold: float = None) -> List[Dict[str, Any]]:
        """
        의미적 검색 실행
        
        Args:
            query: 검색 질문
            k: 반환할 결과 수
            similarity_threshold: 유사도 임계값
            
        Returns:
            검색 결과 리스트
        """
        if k is None:
            k = self.default_k
        if similarity_threshold is None:
            similarity_threshold = self.min_similarity_threshold
        
        logger.info(f"🔍 의미적 검색 시작: '{query}'")
        logger.info(f"  - 검색 결과 수: {k}")
        logger.info(f"  - 유사도 임계값: {similarity_threshold}")
        
        try:
            # 1. 질문 임베딩 생성
            query_embedding = self.generate_query_embedding(query)
            
            # 2. FAISS 유사도 검색
            distances, indices, metadata = self.vector_db.search(query_embedding, k)
            
            # 3. 결과 필터링 및 정리
            filtered_results = []
            for i, meta in enumerate(metadata):
                similarity_score = float(distances[i])
                
                # 유사도 임계값 체크
                if similarity_score >= similarity_threshold:
                    result = {
                        **meta,
                        'similarity_score': similarity_score,
                        'rank': i + 1,
                        'query': query
                    }
                    filtered_results.append(result)
            
            logger.info(f"✅ 검색 완료: {len(filtered_results)}개 결과 (임계값 {similarity_threshold} 이상)")
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"❌ 의미적 검색 실패: {e}")
            return []
    
    def batch_search(self, 
                    queries: List[str], 
                    k: int = None) -> List[List[Dict[str, Any]]]:
        """
        여러 질문에 대한 배치 검색
        
        Args:
            queries: 검색 질문 리스트
            k: 각 질문당 반환할 결과 수
            
        Returns:
            각 질문에 대한 검색 결과 리스트
        """
        if k is None:
            k = self.default_k
        
        logger.info(f"🔍 배치 검색 시작: {len(queries)}개 질문")
        
        try:
            # 1. 모든 질문을 임베딩으로 변환
            query_embeddings = []
            for query in queries:
                embedding = self.generate_query_embedding(query)
                query_embeddings.append(embedding)
            
            query_embeddings = np.array(query_embeddings)
            
            # 2. 배치 검색 실행
            distances, indices, all_metadata = self.vector_db.batch_search(query_embeddings, k)
            
            # 3. 결과 정리
            all_results = []
            for i, (query, query_metadata) in enumerate(zip(queries, all_metadata)):
                query_results = []
                for j, meta in enumerate(query_metadata):
                    result = {
                        **meta,
                        'query': query,
                        'batch_index': i
                    }
                    query_results.append(result)
                all_results.append(query_results)
            
            logger.info(f"✅ 배치 검색 완료: {len(queries)}개 질문 처리")
            
            return all_results
            
        except Exception as e:
            logger.error(f"❌ 배치 검색 실패: {e}")
            return [[] for _ in queries]
    
    def compose_search_context(self, 
                              search_results: List[Dict[str, Any]],
                              max_context_length: int = 2000) -> Dict[str, Any]:
        """
        검색 결과를 컨텍스트로 구성
        
        Args:
            search_results: 검색 결과 리스트
            max_context_length: 최대 컨텍스트 길이
            
        Returns:
            구성된 컨텍스트 정보
        """
        if not search_results:
            return {
                'context_text': "",
                'source_count': 0,
                'total_length': 0,
                'sources': []
            }
        
        logger.info(f"📝 검색 컨텍스트 구성: {len(search_results)}개 결과")
        
        # 1. 결과를 유사도 순으로 정렬
        sorted_results = sorted(search_results, 
                              key=lambda x: x.get('similarity_score', 0), 
                              reverse=True)
        
        # 2. 컨텍스트 텍스트 구성
        context_parts = []
        current_length = 0
        used_sources = []
        
        for i, result in enumerate(sorted_results):
            # 텍스트 내용 추출
            content = result.get('content', result.get('text', ''))
            if not content:
                continue
            
            # 길이 체크
            if current_length + len(content) > max_context_length:
                # 남은 공간에 맞게 텍스트 자르기
                remaining_space = max_context_length - current_length
                if remaining_space > 100:  # 최소 100자는 되어야 의미가 있음
                    content = content[:remaining_space-3] + "..."
                else:
                    break
            
            # 컨텍스트에 추가
            context_parts.append(f"[출처 {i+1}] {content}")
            current_length += len(content)
            
            # 출처 정보 저장
            source_info = {
                'rank': i + 1,
                'similarity_score': result.get('similarity_score', 0),
                'source_type': result.get('type', 'unknown'),
                'metadata': {k: v for k, v in result.items() 
                           if k not in ['content', 'text']}
            }
            used_sources.append(source_info)
        
        # 3. 최종 컨텍스트 구성
        context_text = "\n\n".join(context_parts)
        
        context_info = {
            'context_text': context_text,
            'source_count': len(used_sources),
            'total_length': len(context_text),
            'sources': used_sources,
            'truncated': current_length >= max_context_length
        }
        
        logger.info(f"✅ 컨텍스트 구성 완료:")
        logger.info(f"  - 사용된 출처: {len(used_sources)}개")
        logger.info(f"  - 총 길이: {len(context_text)}자")
        logger.info(f"  - 잘림 여부: {context_info['truncated']}")
        
        return context_info
    
    def advanced_search(self, 
                       query: str,
                       search_type: str = "semantic",
                       filters: Optional[Dict[str, Any]] = None,
                       k: int = None) -> Dict[str, Any]:
        """
        고급 검색 (필터링, 다양한 검색 타입 지원)
        
        Args:
            query: 검색 질문
            search_type: 검색 타입 ("semantic", "keyword", "hybrid")
            filters: 필터 조건
            k: 반환할 결과 수
            
        Returns:
            검색 결과와 컨텍스트 정보
        """
        if k is None:
            k = self.default_k
        
        logger.info(f"🔍 고급 검색: '{query}' (타입: {search_type})")
        
        try:
            # 1. 기본 의미적 검색
            search_results = self.semantic_search(query, k * 2)  # 더 많이 가져와서 필터링
            
            # 2. 필터 적용
            if filters:
                search_results = self._apply_filters(search_results, filters)
            
            # 3. 결과 수 조정
            search_results = search_results[:k]
            
            # 4. 컨텍스트 구성
            context_info = self.compose_search_context(search_results)
            
            # 5. 최종 결과 구성
            result = {
                'query': query,
                'search_type': search_type,
                'results': search_results,
                'context': context_info,
                'metadata': {
                    'total_results': len(search_results),
                    'search_timestamp': datetime.now().isoformat(),
                    'filters_applied': filters is not None
                }
            }
            
            logger.info(f"✅ 고급 검색 완료: {len(search_results)}개 결과")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 고급 검색 실패: {e}")
            return {
                'query': query,
                'search_type': search_type,
                'results': [],
                'context': {'context_text': "", 'source_count': 0},
                'error': str(e)
            }
    
    def _apply_filters(self, 
                      results: List[Dict[str, Any]], 
                      filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        검색 결과에 필터 적용
        
        Args:
            results: 검색 결과 리스트
            filters: 필터 조건
            
        Returns:
            필터링된 결과
        """
        filtered_results = []
        
        for result in results:
            include_result = True
            
            # 타입 필터
            if 'type' in filters:
                if result.get('type') != filters['type']:
                    include_result = False
            
            # 날짜 범위 필터
            if 'date_range' in filters and include_result:
                result_date = result.get('date')
                if result_date:
                    # 날짜 범위 체크 로직 (구현 필요)
                    pass
            
            # 유사도 임계값 필터
            if 'min_similarity' in filters and include_result:
                if result.get('similarity_score', 0) < filters['min_similarity']:
                    include_result = False
            
            if include_result:
                filtered_results.append(result)
        
        logger.info(f"필터 적용: {len(results)} -> {len(filtered_results)}개 결과")
        
        return filtered_results
    
    def get_search_stats(self) -> Dict[str, Any]:
        """
        검색 시스템 통계 정보
        
        Returns:
            통계 정보
        """
        vector_stats = self.vector_db.get_index_stats()
        
        stats = {
            'system_status': 'ready' if vector_stats['status'] == 'ready' else 'not_ready',
            'vector_database': vector_stats,
            'embedding_model': self.embedding_model,
            'default_k': self.default_k,
            'similarity_threshold': self.min_similarity_threshold,
            'components': {
                'embedding_generator': 'loaded' if self.embedding_generator.model else 'not_loaded',
                'vector_database': vector_stats['status'],
                'text_preprocessor': 'ready'
            }
        }
        
        return stats 