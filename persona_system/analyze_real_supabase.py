#!/usr/bin/env python3
"""
실제 Supabase 데이터 분석 스크립트
"""
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv('../.env.local')  # 상위 디렉토리의 .env.local 파일 로드

from supabase_client import SupabaseClient
from models.persona_generator import PersonaGenerator
from utils.text_preprocessor import TextPreprocessor
from utils.emotion_analyzer import EmotionAnalyzer
from utils.topic_analyzer import TopicAnalyzer


def analyze_real_supabase_data():
    """실제 Supabase 데이터 분석"""
    print("🤖 실제 Supabase 데이터 분석 시작\n")
    
    # 환경변수 확인 (실제 .env.local 파일의 키 이름 사용)
    supabase_url = os.getenv('REACT_APP_UPABASE_URL')        # UPABASE로 수정
    supabase_key = os.getenv('REACT_APP_UPABASE_ANON_KEY')   # UPABASE로 수정
    
    print(f"🔍 환경변수 확인:")
    print(f"  • URL: {supabase_url[:50] if supabase_url else 'None'}...")
    print(f"  • KEY: {supabase_key[:50] if supabase_key else 'None'}...")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase 환경변수가 설정되지 않았습니다.")
        print("다음 환경변수를 설정해주세요:")
        print("REACT_APP_UPABASE_URL='your_supabase_url'")
        print("REACT_APP_UPABASE_ANON_KEY='your_supabase_anon_key'")
        return None
    
    try:
        # Supabase 클라이언트 생성
        print("🔗 Supabase에 연결 중...")
        client = SupabaseClient(supabase_url, supabase_key)
        
        # 연결 테스트
        if not client.test_connection():
            print("❌ Supabase 연결에 실패했습니다.")
            return None
        
        print("✅ Supabase 연결 성공!")
        
        # 데이터 수집
        print("\n📊 데이터 수집 중...")
        books = client.get_all_books()
        action_lists = client.get_all_action_lists()
        readers = client.get_all_readers()
        
        if not books:
            print("⚠️  책 데이터가 없습니다.")
            return None
        
        print(f"📚 총 {len(books)}권의 책")
        print(f"🎯 총 {len(action_lists)}개의 액션 리스트")
        print(f"👥 총 {len(readers)}명의 독자")
        
        return {
            "client": client,
            "books": books,
            "action_lists": action_lists,
            "readers": readers
        }
        
    except Exception as e:
        print(f"❌ Supabase 연결 중 오류: {e}")
        return None


def analyze_individual_readers(data):
    """개별 독자별 분석"""
    print("\n=== 📚 개별 독자별 분석 ===\n")
    
    books = data["books"]
    action_lists = data["action_lists"]
    
    # 독자별로 데이터 그룹화
    readers = {}
    for book in books:
        # reader_id 또는 reader 필드 확인
        reader_id = book.get('reader_id') or book.get('reader')
        if reader_id:
            if reader_id not in readers:
                readers[reader_id] = {
                    "books": [],
                    "action_lists": []
                }
            readers[reader_id]["books"].append(book)
    
    # 액션 리스트도 독자별로 분류
    for action in action_lists:
        reader_id = action.get('reader_id') or action.get('reader')
        if reader_id and reader_id in readers:
            readers[reader_id]["action_lists"].append(action)
    
    persona_generator = PersonaGenerator()
    
    for reader_id, reader_data in readers.items():
        print(f"🔍 **독자 ID: {reader_id}**")
        print("-" * 50)
        
        # 독자 이름 찾기
        reader_name = reader_id
        for reader_info in data["readers"]:
            if reader_info.get('id') == reader_id:
                reader_name = reader_info.get('name', reader_id)
                break
        
        print(f"📖 읽은 책 수: {len(reader_data['books'])}")
        print(f"🎯 액션 리스트 수: {len(reader_data['action_lists'])}")
        
        if len(reader_data['books']) > 0:
            # 페르소나 생성
            user_data = {
                "id": reader_id,
                "name": reader_name,
                "books": reader_data["books"],
                "action_lists": reader_data["action_lists"]
            }
            
            try:
                persona = persona_generator.generate_persona(user_data)
                
                print(f"💭 페르소나: {persona['persona_description']}")
                print(f"🎨 성격 특성: {', '.join(persona['personality_traits'])}")
                print(f"📝 의사소통 스타일: {persona['communication_style']['overall_style']}")
                print(f"🌱 성장 영역: {', '.join(persona['growth_areas'])}")
                
                # 상세 분석
                print("\n📊 **상세 분석**")
                print(f"  • 주요 감정: {persona['emotion_profile']['dominant_emotion']}")
                print(f"  • 전체 톤: {persona['emotion_profile']['overall_sentiment']}")
                
                if persona['interests']['top_keywords']:
                    print(f"  • 관심 키워드: {', '.join(persona['interests']['top_keywords'][:5])}")
                
                # 독서 패턴 분석
                if reader_data["books"]:
                    ratings = [book.get("rating", 0) for book in reader_data["books"] if book.get("rating")]
                    emotions = [book.get("emotion", "unknown") for book in reader_data["books"] if book.get("emotion")]
                    genres = [book.get("genre", "unknown") for book in reader_data["books"] if book.get("genre")]
                    
                    if ratings:
                        print(f"\n📈 **독서 패턴**")
                        print(f"  • 평균 평점: {sum(ratings) / len(ratings):.1f}")
                        if genres:
                            print(f"  • 선호 장르: {', '.join(set(genres))}")
                        if emotions:
                            print(f"  • 감정 분포: {', '.join(set(emotions))}")
                
            except Exception as e:
                print(f"❌ 페르소나 생성 실패: {e}")
        
        print("\n" + "=" * 60)
        print()


def analyze_group_patterns(data):
    """그룹 전체 패턴 분석"""
    print("\n=== 🏘️ 그룹 전체 패턴 분석 ===\n")
    
    books = data["books"]
    
    # 전체 통계
    total_books = len(books)
    total_actions = len(data["action_lists"])
    
    print(f"📚 **전체 통계**")
    print(f"  • 총 독서 기록: {total_books}권")
    print(f"  • 총 액션 리스트: {total_actions}개")
    print()
    
    if total_books == 0:
        print("⚠️  분석할 책 데이터가 없습니다.")
        return
    
    # 장르별 분석
    genres = {}
    emotions = {}
    ratings = []
    tags = []
    
    for book in books:
        genre = book.get("genre", "unknown")
        emotion = book.get("emotion", "unknown")
        rating = book.get("rating", 0)
        book_tags = book.get("tags", [])
        
        genres[genre] = genres.get(genre, 0) + 1
        emotions[emotion] = emotions.get(emotion, 0) + 1
        if rating > 0:
            ratings.append(rating)
        if book_tags:
            tags.extend(book_tags)
    
    print(f"🎭 **장르별 분포**")
    for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_books) * 100
        print(f"  • {genre}: {count}권 ({percentage:.1f}%)")
    print()
    
    print(f"😊 **감정별 분포**")
    for emotion, count in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_books) * 100
        print(f"  • {emotion}: {count}권 ({percentage:.1f}%)")
    print()
    
    if ratings:
        print(f"⭐ **평점 분석**")
        print(f"  • 평균 평점: {sum(ratings) / len(ratings):.2f}")
        print(f"  • 최고 평점: {max(ratings)}")
        print(f"  • 최저 평점: {min(ratings)}")
        print()
    
    # 태그 분석
    if tags:
        tag_counts = {}
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        print(f"🏷️ **인기 태그**")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {tag}: {count}회")
        print()


def generate_recommendations(data):
    """개인 맞춤형 추천 생성"""
    print("\n=== 🎯 개인 맞춤형 추천 ===\n")
    
    books = data["books"]
    
    # 독자별로 추천 생성
    readers = {}
    for book in books:
        reader_id = book.get('reader_id') or book.get('reader')
        if reader_id:
            if reader_id not in readers:
                readers[reader_id] = {"books": []}
            readers[reader_id]["books"].append(book)
    
    if not readers:
        print("⚠️  독자 데이터가 없습니다.")
        return
    
    for reader_id, reader_data in readers.items():
        # 독자 이름 찾기
        reader_name = reader_id
        for reader_info in data["readers"]:
            if reader_info.get('id') == reader_id:
                reader_name = reader_info.get('name', reader_id)
                break
        
        print(f"🎁 **{reader_name}님을 위한 추천**")
        print("-" * 40)
        
        if len(reader_data["books"]) > 0:
            # 독서 패턴 분석
            genres = [book.get("genre", "unknown") for book in reader_data["books"] if book.get("genre")]
            emotions = [book.get("emotion", "unknown") for book in reader_data["books"] if book.get("emotion")]
            ratings = [book.get("rating", 0) for book in reader_data["books"] if book.get("rating")]
            
            # 선호 장르 파악
            genre_preferences = {}
            for genre in genres:
                genre_preferences[genre] = genre_preferences.get(genre, 0) + 1
            
            # 선호 감정 파악
            emotion_preferences = {}
            for emotion in emotions:
                emotion_preferences[emotion] = emotion_preferences.get(emotion, 0) + 1
            
            # 추천 로직
            print(f"📖 **독서 패턴**")
            if genre_preferences:
                print(f"  • 선호 장르: {', '.join(sorted(genre_preferences.keys()))}")
            if emotion_preferences:
                print(f"  • 선호 감정: {', '.join(sorted(emotion_preferences.keys()))}")
            if ratings:
                print(f"  • 평균 평점: {sum(ratings) / len(ratings):.1f}")
            print()
            
            print(f"💡 **추천 아이디어**")
            
            # 장르 기반 추천
            if "science" in genre_preferences:
                print(f"  • 과학 분야 확장: 우주, 생물학, 화학 등 관련 분야 탐색")
            if "novel" in genre_preferences:
                print(f"  • 문학 세계 확장: 현대문학, 고전문학, 세계문학 등")
            if "philosophy" in genre_preferences:
                print(f"  • 철학 심화: 동양철학, 서양철학, 현대철학 등")
            if "history" in genre_preferences:
                print(f"  • 역사 심화: 고대사, 근현대사, 세계사 등")
            
            # 감정 기반 추천
            if "excited" in emotion_preferences:
                print(f"  • 모험/액션 장르: 스릴과 긴장감을 주는 작품")
            if "thoughtful" in emotion_preferences:
                print(f"  • 사색적 작품: 깊이 있는 사고를 자극하는 책")
            if "calm" in emotion_preferences:
                print(f"  • 평온한 작품: 마음의 평화를 찾을 수 있는 책")
            if "surprised" in emotion_preferences:
                print(f"  • 놀라운 작품: 예상치 못한 반전과 깨달음을 주는 책")
        
        print()
        print("=" * 50)
        print()


def export_analysis_results(data, analysis_data):
    """분석 결과 내보내기"""
    print("\n=== 📁 분석 결과 내보내기 ===\n")
    
    try:
        # 분석 결과를 JSON 파일로 저장
        output_file = f"real_supabase_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "analysis_time": datetime.now().isoformat(),
            "data_summary": {
                "total_books": len(data["books"]),
                "total_action_lists": len(data["action_lists"]),
                "total_readers": len(data["readers"]),
                "readers": list(set([book.get('reader_id') or book.get('reader') for book in data["books"] if book.get('reader_id') or book.get('reader')]))
            },
            "analysis_results": analysis_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 분석 결과가 {output_file}에 저장되었습니다.")
        
        # Supabase 데이터도 별도로 내보내기
        if data["client"]:
            data["client"].export_data_to_json(f"supabase_raw_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
    except Exception as e:
        print(f"❌ 결과 내보내기 실패: {e}")


def main():
    """메인 함수"""
    print("🤖 실제 Supabase 데이터 분석 시작\n")
    
    try:
        # 1. Supabase 데이터 수집
        data = analyze_real_supabase_data()
        if not data:
            print("❌ 데이터 수집에 실패했습니다.")
            return
        
        print(f"📊 분석 대상: Supabase 독서 데이터")
        print(f"📅 분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 2. 개별 독자별 분석
        analyze_individual_readers(data)
        
        # 3. 그룹 전체 패턴 분석
        analyze_group_patterns(data)
        
        # 4. 개인 맞춤형 추천
        generate_recommendations(data)
        
        print("✅ 실제 Supabase 데이터 분석이 완료되었습니다!")
        
        # 5. 결과 내보내기
        export_analysis_results(data, {
            "individual_analysis": "완료",
            "group_patterns": "완료",
            "recommendations": "완료"
        })
        
    except Exception as e:
        print(f"❌ 분석 중 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 