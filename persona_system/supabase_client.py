"""
Supabase 클라이언트 - 실제 데이터베이스 연동
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv('../.env.local')  # 상위 디렉토리의 .env.local 파일 로드

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  supabase-py가 설치되지 않았습니다. pip install supabase로 설치해주세요.")


class SupabaseClient:
    """Supabase 데이터베이스 클라이언트"""
    
    def __init__(self, url: str = None, key: str = None):
        """초기화"""
        # 환경변수에서 기본값 가져오기 (실제 .env.local 파일의 키 이름 사용)
        self.url = url or os.getenv('REACT_APP_UPABASE_URL')
        self.key = key or os.getenv('REACT_APP_UPABASE_ANON_KEY')
        self.client = None
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL과 API 키가 필요합니다. 환경변수 REACT_APP_UPABASE_URL, REACT_APP_UPABASE_ANON_KEY를 설정하거나 직접 전달해주세요.")
        
        if SUPABASE_AVAILABLE:
            try:
                self.client = create_client(self.url, self.key)
                print("✅ Supabase 연결 성공!")
            except Exception as e:
                print(f"❌ Supabase 연결 실패: {e}")
                self.client = None
        else:
            print("❌ supabase-py 라이브러리가 설치되지 않았습니다.")
    
    def test_connection(self) -> bool:
        """연결 테스트"""
        if not self.client:
            return False
        
        try:
            # 간단한 쿼리로 연결 테스트
            print("🔍 연결 테스트 중...")
            response = self.client.table('books').select('id').limit(1).execute()
            print("✅ 연결 테스트 성공!")
            return True
        except Exception as e:
            print(f"⚠️  연결 테스트 경고: {e}")
            # 연결 테스트가 실패해도 클라이언트는 유효할 수 있음
            # 실제 데이터 가져오기 시도
            try:
                print("🔄 실제 데이터 가져오기로 연결 확인...")
                response = self.client.table('books').select('*').limit(1).execute()
                print("✅ 실제 데이터 가져오기 성공!")
                return True
            except Exception as e2:
                print(f"❌ 실제 데이터 가져오기 실패: {e2}")
                return False
    
    def get_all_books(self) -> List[Dict[str, Any]]:
        """모든 책 데이터 가져오기"""
        if not self.client:
            return []
        
        try:
            response = self.client.table('books').select('*').execute()
            books = response.data if hasattr(response, 'data') else []
            print(f"📚 총 {len(books)}권의 책을 가져왔습니다.")
            return books
        except Exception as e:
            print(f"책 데이터 가져오기 실패: {e}")
            return []
    
    def get_all_action_lists(self) -> List[Dict[str, Any]]:
        """모든 액션 리스트 가져오기"""
        if not self.client:
            return []
        
        try:
            response = self.client.table('action_lists').select('*').execute()
            actions = response.data if hasattr(response, 'data') else []
            print(f"🎯 총 {len(actions)}개의 액션 리스트를 가져왔습니다.")
            return actions
        except Exception as e:
            print(f"액션 리스트 가져오기 실패: {e}")
            return []
    
    def get_all_readers(self) -> List[Dict[str, Any]]:
        """모든 독자 정보 가져오기"""
        if not self.client:
            return []
        
        try:
            response = self.client.table('readers').select('*').execute()
            readers = response.data if hasattr(response, 'data') else []
            print(f"👥 총 {len(readers)}명의 독자를 가져왔습니다.")
            return readers
        except Exception as e:
            print(f"독자 정보 가져오기 실패: {e}")
            return []
    
    def get_books_by_reader(self, reader_id: str) -> List[Dict[str, Any]]:
        """특정 독자의 책 목록 가져오기"""
        if not self.client:
            return []
        
        try:
            response = self.client.table('books').select('*').eq('reader_id', reader_id).execute()
            books = response.data if hasattr(response, 'data') else []
            print(f"📖 독자 {reader_id}의 책 {len(books)}권을 가져왔습니다.")
            return books
        except Exception as e:
            print(f"독자별 책 데이터 가져오기 실패: {e}")
            return []
    
    def get_action_lists_by_reader(self, reader_id: str) -> List[Dict[str, Any]]:
        """특정 독자의 액션 리스트 가져오기"""
        if not self.client:
            return []
        
        try:
            response = self.client.table('action_lists').select('*').eq('reader_id', reader_id).execute()
            actions = response.data if hasattr(response, 'data') else []
            print(f"🎯 독자 {reader_id}의 액션 리스트 {len(actions)}개를 가져왔습니다.")
            return actions
        except Exception as e:
            print(f"독자별 액션 리스트 가져오기 실패: {e}")
            return []
    
    def get_recent_books(self, days: int = 30) -> List[Dict[str, Any]]:
        """최근 N일간의 책 데이터 가져오기"""
        if not self.client:
            return []
        
        try:
            # 최근 N일 계산
            from datetime import datetime, timedelta
            recent_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            response = self.client.table('books').select('*').gte('created_at', recent_date).execute()
            books = response.data if hasattr(response, 'data') else []
            print(f"📚 최근 {days}일간의 책 {len(books)}권을 가져왔습니다.")
            return books
        except Exception as e:
            print(f"최근 책 데이터 가져오기 실패: {e}")
            return []
    
    def get_books_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """특정 장르의 책 가져오기"""
        if not self.client:
            return []
        
        try:
            response = self.client.table('books').select('*').eq('genre', genre).execute()
            books = response.data if hasattr(response, 'data') else []
            print(f"📚 {genre} 장르의 책 {len(books)}권을 가져왔습니다.")
            return books
        except Exception as e:
            print(f"장르별 책 데이터 가져오기 실패: {e}")
            return []
    
    def get_books_by_emotion(self, emotion: str) -> List[Dict[str, Any]]:
        """특정 감정의 책 가져오기"""
        if not self.client:
            return []
        
        try:
            response = self.client.table('books').select('*').eq('emotion', emotion).execute()
            books = response.data if hasattr(response, 'data') else []
            print(f"📚 {emotion} 감정의 책 {len(books)}권을 가져왔습니다.")
            return books
        except Exception as e:
            print(f"감정별 책 데이터 가져오기 실패: {e}")
            return []
    
    def get_database_schema(self) -> Dict[str, Any]:
        """데이터베이스 스키마 정보 가져오기"""
        if not self.client:
            return {}
        
        try:
            # 테이블 목록 가져오기 (실제로는 RPC 함수나 다른 방법 필요)
            print("📋 데이터베이스 스키마 정보를 가져오는 중...")
            
            # 기본 테이블 정보
            schema_info = {
                "tables": {
                    "books": "독서 기록 테이블",
                    "readers": "독자 정보 테이블", 
                    "action_lists": "액션 리스트 테이블"
                },
                "connection_status": "connected",
                "timestamp": datetime.now().isoformat()
            }
            
            return schema_info
        except Exception as e:
            print(f"스키마 정보 가져오기 실패: {e}")
            return {}
    
    def export_data_to_json(self, filename: str = "supabase_export.json") -> bool:
        """모든 데이터를 JSON 파일로 내보내기"""
        if not self.client:
            return False
        
        try:
            # 모든 데이터 수집
            books = self.get_all_books()
            actions = self.get_all_action_lists()
            readers = self.get_all_readers()
            
            export_data = {
                "export_time": datetime.now().isoformat(),
                "books": books,
                "action_lists": actions,
                "readers": readers,
                "total_count": {
                    "books": len(books),
                    "action_lists": len(actions),
                    "readers": len(readers)
                }
            }
            
            # JSON 파일로 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 데이터가 {filename}에 성공적으로 내보내졌습니다.")
            return True
            
        except Exception as e:
            print(f"데이터 내보내기 실패: {e}")
            return False


def main():
    """테스트 함수"""
    print("🔗 Supabase 클라이언트 테스트")
    
    # 환경변수 확인
    supabase_url = os.getenv('REACT_APP_UPABASE_URL')
    supabase_key = os.getenv('REACT_APP_UPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ 환경변수가 설정되지 않았습니다.")
        print("다음 환경변수를 설정해주세요:")
        print("export REACT_APP_UPABASE_URL='your_supabase_url'")
        print("export REACT_APP_UPABASE_ANON_KEY='your_supabase_anon_key'")
        return
    
    try:
        # 클라이언트 생성
        client = SupabaseClient(supabase_url, supabase_key)
        
        # 연결 테스트
        if client.test_connection():
            print("✅ Supabase 연결 성공!")
            
            # 스키마 정보
            schema = client.get_database_schema()
            print(f"📋 스키마 정보: {schema}")
            
            # 데이터 내보내기
            client.export_data_to_json()
            
        else:
            print("❌ Supabase 연결 실패!")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    main() 