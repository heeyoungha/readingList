"""
S3 호환 저장소 매니저 - 로컬과 클라우드 저장소 추상화
"""
import os
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import numpy as np
from loguru import logger


class StorageManager:
    """S3 호환 저장소 매니저"""
    
    def __init__(self, 
                 storage_type: str = "local",
                 base_path: str = "./data",
                 s3_bucket: str = None,
                 s3_region: str = "ap-northeast-2"):
        """
        저장소 매니저 초기화
        
        Args:
            storage_type: 저장소 타입 ("local", "s3", "hybrid")
            base_path: 로컬 기본 경로
            s3_bucket: S3 버킷명
            s3_region: S3 리전
        """
        self.storage_type = storage_type
        self.base_path = Path(base_path)
        self.s3_bucket = s3_bucket
        self.s3_region = s3_region
        
        # S3 클라이언트 초기화
        self.s3_client = None
        if storage_type in ["s3", "hybrid"]:
            self._init_s3_client()
        
        # 디렉토리 구조 생성
        self._create_directory_structure()
        
        logger.info(f"저장소 매니저 초기화 완료: {storage_type}")
    
    def _init_s3_client(self):
        """S3 클라이언트 초기화"""
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.s3_region
            )
            logger.info(f"S3 클라이언트 초기화 완료: {self.s3_region}")
        except NoCredentialsError:
            logger.warning("AWS 자격 증명을 찾을 수 없습니다. 환경 변수를 확인하세요.")
            self.s3_client = None
        except Exception as e:
            logger.error(f"S3 클라이언트 초기화 실패: {e}")
            self.s3_client = None
    
    def _create_directory_structure(self):
        """로컬 디렉토리 구조 생성"""
        directories = [
            "users",
            "global/models",
            "global/embeddings", 
            "global/vector_indexes",
            "cache",
            "logs"
        ]
        
        for dir_path in directories:
            (self.base_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    def get_user_path(self, user_id: str, data_type: str, version: str = "latest") -> Dict[str, str]:
        """
        사용자별 데이터 경로 생성
        
        Args:
            user_id: 사용자 ID
            data_type: 데이터 타입 (embeddings, personas, chat_history 등)
            version: 버전 (latest, 날짜 등)
        
        Returns:
            경로 정보 딕셔너리
        """
        if self.storage_type == "local":
            base_path = self.base_path / "users" / user_id / data_type
            if version == "latest":
                path = base_path / "latest"
            else:
                path = base_path / "history" / version
            
            return {
                'local_path': str(path),
                's3_key': f"users/{user_id}/{data_type}/{version}",
                'type': 'local'
            }
        
        elif self.storage_type == "s3":
            s3_key = f"users/{user_id}/{data_type}/{version}"
            return {
                'local_path': str(self.base_path / "cache" / user_id / data_type / version),
                's3_key': s3_key,
                'type': 's3'
            }
        
        else:  # hybrid
            local_path = self.base_path / "users" / user_id / data_type / version
            s3_key = f"users/{user_id}/{data_type}/{version}"
            return {
                'local_path': str(local_path),
                's3_key': s3_key,
                'type': 'hybrid'
            }
    
    def save_user_embeddings(self, user_id: str, embeddings_data: Dict[str, Any], 
                            version: str = None) -> bool:
        """
        사용자 임베딩 저장
        
        Args:
            user_id: 사용자 ID
            embeddings_data: 임베딩 데이터
            version: 버전 (None이면 현재 날짜)
        
        Returns:
            저장 성공 여부
        """
        if version is None:
            version = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        paths = self.get_user_path(user_id, "embeddings", version)
        
        try:
            # 로컬 저장
            if self.storage_type in ["local", "hybrid"]:
                self._save_local_embeddings(paths['local_path'], embeddings_data)
            
            # S3 저장
            if self.storage_type in ["s3", "hybrid"] and self.s3_client:
                self._save_s3_embeddings(paths['s3_key'], embeddings_data)
            
            # 최신 버전 링크 업데이트
            self._update_latest_version(user_id, "embeddings", version)
            
            logger.info(f"사용자 임베딩 저장 완료: {user_id}, 버전: {version}")
            return True
            
        except Exception as e:
            logger.error(f"사용자 임베딩 저장 실패: {e}")
            return False
    
    def _save_local_embeddings(self, local_path: str, embeddings_data: Dict[str, Any]):
        """로컬에 임베딩 저장"""
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 임베딩 벡터 저장 (.npy)
        embeddings_path = local_path.with_suffix('.npy')
        np.save(embeddings_path, embeddings_data['embeddings'])
        
        # 메타데이터 저장 (.json)
        metadata_path = local_path.with_suffix('.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'chunks': embeddings_data['chunks'],
                'metadata': embeddings_data['metadata'],
                'text_sources': embeddings_data.get('text_sources', []),
                'model_name': embeddings_data['model_name'],
                'embedding_dim': embeddings_data['embedding_dim'],
                'chunk_count': len(embeddings_data['chunks']),
                'created_at': datetime.now().isoformat(),
                'version': embeddings_data.get('version', 'unknown')
            }, f, ensure_ascii=False, indent=2)
    
    def _save_s3_embeddings(self, s3_key: str, embeddings_data: Dict[str, Any]):
        """S3에 임베딩 저장"""
        if not self.s3_client:
            return
        
        try:
            # 임베딩 벡터를 바이트로 변환
            embeddings_bytes = embeddings_data['embeddings'].tobytes()
            
            # S3에 업로드
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=f"{s3_key}.npy",
                Body=embeddings_bytes
            )
            
            # 메타데이터 업로드
            metadata = {
                'chunks': embeddings_data['chunks'],
                'metadata': embeddings_data['metadata'],
                'text_sources': embeddings_data.get('text_sources', []),
                'model_name': embeddings_data['model_name'],
                'embedding_dim': embeddings_data['embedding_dim'],
                'chunk_count': len(embeddings_data['chunks']),
                'created_at': datetime.now().isoformat(),
                'version': embeddings_data.get('version', 'unknown')
            }
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=f"{s3_key}.json",
                Body=json.dumps(metadata, ensure_ascii=False, indent=2),
                ContentType='application/json'
            )
            
        except ClientError as e:
            logger.error(f"S3 저장 실패: {e}")
            raise
    
    def load_user_embeddings(self, user_id: str, version: str = "latest") -> Optional[Dict[str, Any]]:
        """
        사용자 임베딩 로드
        
        Args:
            user_id: 사용자 ID
            version: 버전 (latest 또는 특정 날짜)
        
        Returns:
            임베딩 데이터 또는 None
        """
        paths = self.get_user_path(user_id, "embeddings", version)
        
        try:
            if self.storage_type == "local":
                return self._load_local_embeddings(paths['local_path'])
            
            elif self.storage_type == "s3":
                return self._load_s3_embeddings(paths['s3_key'])
            
            else:  # hybrid - 로컬 먼저 시도, 없으면 S3에서 다운로드
                local_data = self._load_local_embeddings(paths['local_path'])
                if local_data:
                    return local_data
                
                # S3에서 다운로드하여 로컬에 캐시
                s3_data = self._load_s3_embeddings(paths['s3_key'])
                if s3_data:
                    self._save_local_embeddings(paths['local_path'], s3_data)
                    return s3_data
                
        except Exception as e:
            logger.error(f"사용자 임베딩 로드 실패: {e}")
        
        return None
    
    def _load_local_embeddings(self, local_path: str) -> Optional[Dict[str, Any]]:
        """로컬에서 임베딩 로드"""
        local_path = Path(local_path)
        
        embeddings_path = local_path.with_suffix('.npy')
        metadata_path = local_path.with_suffix('.json')
        
        if not embeddings_path.exists() or not metadata_path.exists():
            return None
        
        try:
            # 임베딩 벡터 로드
            embeddings = np.load(embeddings_path)
            
            # 메타데이터 로드
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            return {
                'embeddings': embeddings,
                'chunks': metadata['chunks'],
                'metadata': metadata['metadata'],
                'text_sources': metadata.get('text_sources', []),
                'model_name': metadata['model_name'],
                'embedding_dim': metadata['embedding_dim']
            }
            
        except Exception as e:
            logger.error(f"로컬 임베딩 로드 실패: {e}")
            return None
    
    def _load_s3_embeddings(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """S3에서 임베딩 로드"""
        if not self.s3_client:
            return None
        
        try:
            # 메타데이터 로드
            response = self.s3_client.get_object(
                Bucket=self.s3_bucket,
                Key=f"{s3_key}.json"
            )
            metadata = json.loads(response['Body'].read().decode('utf-8'))
            
            # 임베딩 벡터 로드
            response = self.s3_client.get_object(
                Bucket=self.s3_bucket,
                Key=f"{s3_key}.npy"
            )
            embeddings_bytes = response['Body'].read()
            embeddings = np.frombuffer(embeddings_bytes, dtype=np.float32).reshape(
                metadata['chunk_count'], metadata['embedding_dim']
            )
            
            return {
                'embeddings': embeddings,
                'chunks': metadata['chunks'],
                'metadata': metadata['metadata'],
                'text_sources': metadata.get('text_sources', []),
                'model_name': metadata['model_name'],
                'embedding_dim': metadata['embedding_dim']
            }
            
        except ClientError as e:
            logger.error(f"S3 임베딩 로드 실패: {e}")
            return None
    
    def _update_latest_version(self, user_id: str, data_type: str, version: str):
        """최신 버전 링크 업데이트"""
        latest_paths = self.get_user_path(user_id, data_type, "latest")
        
        if self.storage_type in ["local", "hybrid"]:
            latest_path = Path(latest_paths['local_path'])
            latest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 심볼릭 링크 또는 복사
            target_path = Path(latest_paths['local_path']).parent.parent / version
            if latest_path.exists():
                latest_path.unlink()
            latest_path.symlink_to(target_path)
    
    def save_user_persona(self, user_id: str, persona_data: Dict[str, Any]) -> bool:
        """사용자 페르소나 저장"""
        paths = self.get_user_path(user_id, "personas", "latest")
        
        try:
            if self.storage_type in ["local", "hybrid"]:
                local_path = Path(paths['local_path'])
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(local_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
                    json.dump(persona_data, f, ensure_ascii=False, indent=2)
            
            if self.storage_type in ["s3", "hybrid"] and self.s3_client:
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=f"{paths['s3_key']}.json",
                    Body=json.dumps(persona_data, ensure_ascii=False, indent=2),
                    ContentType='application/json'
                )
            
            logger.info(f"사용자 페르소나 저장 완료: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"사용자 페르소나 저장 실패: {e}")
            return False
    
    def save_chat_history(self, user_id: str, chat_data: Dict[str, Any]) -> bool:
        """채팅 기록 저장"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        paths = self.get_user_path(user_id, "chat_history", timestamp)
        
        try:
            if self.storage_type in ["local", "hybrid"]:
                local_path = Path(paths['local_path'])
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(local_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
                    json.dump(chat_data, f, ensure_ascii=False, indent=2)
            
            if self.storage_type in ["s3", "hybrid"] and self.s3_client:
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=f"{paths['s3_key']}.json",
                    Body=json.dumps(chat_data, ensure_ascii=False, indent=2),
                    ContentType='application/json'
                )
            
            logger.info(f"채팅 기록 저장 완료: {user_id}, 시간: {timestamp}")
            return True
            
        except Exception as e:
            logger.error(f"채팅 기록 저장 실패: {e}")
            return False
    
    def get_user_data_summary(self, user_id: str) -> Dict[str, Any]:
        """사용자 데이터 요약 정보 반환"""
        summary = {
            'user_id': user_id,
            'embeddings': [],
            'personas': [],
            'chat_history': [],
            'recommendations': []
        }
        
        try:
            # S3에서 사용자 데이터 목록 조회
            if self.storage_type in ["s3", "hybrid"] and self.s3_client:
                prefix = f"users/{user_id}/"
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix=prefix
                )
                
                for obj in response.get('Contents', []):
                    key = obj['Key']
                    if 'embeddings' in key:
                        summary['embeddings'].append(key.split('/')[-1])
                    elif 'personas' in key:
                        summary['personas'].append(key.split('/')[-1])
                    elif 'chat_history' in key:
                        summary['chat_history'].append(key.split('/')[-1])
            
            # 로컬에서도 확인
            if self.storage_type in ["local", "hybrid"]:
                user_path = self.base_path / "users" / user_id
                if user_path.exists():
                    for data_type in ['embeddings', 'personas', 'chat_history']:
                        type_path = user_path / data_type
                        if type_path.exists():
                            for item in type_path.iterdir():
                                if item.is_file():
                                    summary[data_type].append(item.name)
            
        except Exception as e:
            logger.error(f"사용자 데이터 요약 조회 실패: {e}")
        
        return summary 